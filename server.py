import socket
import random

class Server:
    def __init__(self, host_ip, welcome_port):
        self.host_ip = host_ip
        self.welcome_port = welcome_port
        self.ports_used = [welcome_port]
        self.sockets_used = []

    def get_new_port(self):
        while True:
            num = random.randint(1024, 65535)
            if num not in self.ports_used:
                self.ports_used.append(num)
                return num

    @staticmethod
    def encode(packet_type, source, dest, data=""):
        line2str = ""
        if packet_type == "ack":
            line2str = "1000"
        elif packet_type == "syn":
            line2str = "0100"
        elif packet_type == "fin":
            line2str = "0010"
        elif packet_type == "urg":
            line2str = "0001"
        elif packet_type == "syn/ack":
            line2str = "1001"
        elif packet_type is None:
            line2str = "0000"
        header = '{0:016b}'.format(source) + '{0:016b}'.format(dest) + line2str + str(data)
        return header.encode()

    @staticmethod
    def decode(message):
        message = message.decode()
        message_type = ""
        if int(message[35]) == 1 and int(message[32]) == 1:
            message_type = "syn/ack"
        elif int(message[33]) == 1:
            message_type = "syn"
        elif int(message[34]) == 1:
            message_type = "fin"
        elif int(message[35]) == 1:
            message_type = "urg"
        elif int(message[32]) == 1:
            message_type = "ack"
        return {"source": int(message[:16], 2), "dest": int(message[16:32], 2), "message type": message_type,
                "data": message[36:]}

    def new_socket(self, s, port, client_port):
        try:
            s.listen(1)
            s, addr = s.accept()
            print(f"Port {port} is listening")
            while True:
                message = s.recv(1024)
                message = self.decode(message)
                if message["data"] == "ping":
                    print(f"Server at port {port} received ping from client at {client_port}")
                    message = self.encode(None, port, client_port, "pong")
                    s.sendto(message, (self.host_ip, client_port))
        except KeyboardInterrupt:
            s.close()

    def welcome(self):
        welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        welcome_socket.bind((self.host_ip, self.welcome_port))
        self.sockets_used.append(welcome_socket)
        welcome_socket.listen(1)
        welcome_socket, addr = welcome_socket.accept()
        print("Listening")
        try:
            message = welcome_socket.recv(1024)
            self.ports_used.append(addr[1])
            message = self.decode(message)
            if message["message type"] == "syn":
                new_port = self.get_new_port()
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.bind((self.host_ip, new_port))
                print(f"Received SYN, sending SYN/ACK, new port created at {new_port}")
                message = self.encode("syn/ack", self.welcome_port, addr[1], str(new_port))
                welcome_socket.sendto(message, addr)
                message = welcome_socket.recv(1024)
                message = self.decode(message)
                if message["message type"] == "ack":
                    new_client_port = int(message["data"])
                    self.new_socket(new_socket, new_port, new_client_port)
        except KeyboardInterrupt:
            welcome_socket.close()

    def run(self):
        self.welcome()


def main():
    ip = "192.168.0.136"
    server_welcome_port = 65432
    server = Server(ip, server_welcome_port)
    server.run()


main()