import socket
from _helper import encode, decode
import sys


class Client:
    def __init__(self, host_ip, server_welcome_port):
        self.host_ip = host_ip
        self.server_welcome_port = server_welcome_port

    def new_socket(self, s, port, server_port, domain):
        try:
            message = encode(None, port, server_port, "ping")
            s.sendto(message, (self.host_ip, server_port))
            port = s.getsockname()[1]
            while True:
                message, server_address = s.recvfrom(1024)
                message = decode(message)
                if message["message type"] == "" and message["data"] == "pong":
                    print(f"Client at port {port} received pong from server at {server_address}")
                    message = encode(None, port, server_port, "ping")
                    s.sendto(message, (self.host_ip, server_port))
                elif message["message type"] == "fin":
                    print(f"Client at port {port} received fin from server at {server_address}")
                    message = encode("ack", port, server_port)
                    s.sendto(message, (self.host_ip, server_port))
                    print(f"Closing Client port at {port}")
                    s.close()
                    break
        except KeyboardInterrupt:
            print(f"Client port at {port} is closing, sending fin to server at {server_address}")
            message = encode("fin", port, server_port)
            s.sendto(message, (self.host_ip, server_port))
            while True:
                message, server_address = s.recvfrom(1024)
                message = decode(message)
                if message["message type"] == "ack":
                    print(f"Received ack from server at {server_address}, closing server at port {port}")
                    s.close()
                    break

    def welcome(self):
        welcome_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        welcome_port = welcome_socket.getsockname()[1]
        message = encode("syn", welcome_port, self.server_welcome_port)
        welcome_socket.sendto(message, (self.host_ip, self.server_welcome_port))
        message, server_address = welcome_socket.recvfrom(1024)
        message = decode(message)
        if message["message type"] == "syn/ack":
            new_server_port = int(message["data"])
            new_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            new_port = new_socket.getsockname()[1]
            print(f"Received SYN/ACK, new server port at {new_server_port}, created new port at {new_port}")
            message = encode("ack", new_port, self.server_welcome_port, str(new_port))
            welcome_socket.sendto(message, (self.host_ip, self.server_welcome_port))
            self.new_socket(new_socket, new_port, new_server_port, domain="tmz.com")
        welcome_socket.close()

    def run(self):
        self.welcome()


def main():
    args = sys.argv
    ip = args[1]
    server_welcome_port = int(args[2])
    client = Client(ip, server_welcome_port)
    client.run()


main()
