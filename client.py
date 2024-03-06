import socket
import random
import time


class Client:
    def __init__(self, host_ip, server_welcome_port):
        self.host_ip = host_ip
        self.server_welcome_port = server_welcome_port
        self.ports_used = [server_welcome_port]
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

    def new_socket(self, s, port, server_port, domain):
        try:
            s.connect((self.host_ip, server_port))
            time.sleep(3)
            while True:
                message = self.encode(None, port, server_port, "ping")
                s.sendto(message, (self.host_ip, server_port))
                message = s.recv(1024)
                message = self.decode(message)
                if message["data"] == "pong":
                    print(f"Client at port {port} received pong from server at {server_port}")
        except KeyboardInterrupt:
            s.close()

    def welcome(self):
        welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        welcome_port = welcome_socket.getsockname()[1]
        welcome_socket.bind((self.host_ip, welcome_port))
        self.ports_used.append(welcome_port)
        self.sockets_used.append(welcome_socket)
        try:
            # domain = input("Please input a website name: ")
            welcome_socket.connect((self.host_ip, self.server_welcome_port))
            print("Sending SYN")
            message = self.encode("syn", welcome_port, self.server_welcome_port)
            welcome_socket.sendto(message, (self.host_ip, self.server_welcome_port))
            data = welcome_socket.recv(1024)
            data = self.decode(data)
            if data["message type"] == "syn/ack":
                new_server_port = int(data["data"])
                self.ports_used.append(new_server_port)
                print(f"Received SYN/ACK, new server port at {new_server_port}")
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_port = self.get_new_port()
                new_socket.bind((self.host_ip, new_port))
                self.sockets_used.append(new_socket)
                print(f"New Socket Created at Port {new_port}, sending ACK")
                message = self.encode("ack", new_port, self.server_welcome_port, str(new_port))
                welcome_socket.sendto(message, (self.host_ip, self.server_welcome_port))
                self.new_socket(new_socket, new_port, new_server_port, domain="tmz.com")
        except KeyboardInterrupt:
            welcome_socket.close()

    def run(self):
        self.welcome()


def main():
    ip = "192.168.0.136"
    server_welcome_port = 65432
    client = Client(ip, server_welcome_port)
    client.run()

main()