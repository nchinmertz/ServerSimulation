import socket
from _helper import decode, encode
import random
import sys
from _thread import *
import threading

print_lock = threading.Lock()


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

    def new_socket(self, s, port, client_port):
        self.sockets_used.append(s)
        try:
            print(f"Port {port} is listening")
            while True:
                message, client_address = s.recvfrom(1024)
                client_port = client_address[1]
                message = decode(message)
                if message["message type"] == "" and message["data"] == "ping":
                    print(f"Server at port {port} received ping from client at {client_address}")
                    message = encode(None, port, client_port, "pong")
                    s.sendto(message, (self.host_ip, client_port))
                elif message["message type"] == "fin":
                    print(f"Server at port {port} received fin from client at {client_address}")
                    message = encode("ack", port, client_port)
                    s.sendto(message, (self.host_ip, client_port))
                    print(f"Closing Server at port {port}")
                    self.sockets_used.remove(s)
                    self.ports_used.remove(port)
                    s.close()
                    return
                else:
                    continue
        except KeyboardInterrupt:
            print(f"Server at port {port} is closing sending fin to client at {client_address}")
            message = encode("fin", port, client_port)
            s.sendto(message, (self.host_ip, client_port))
            while True:
                message, client_address = s.recvfrom(1024)
                message = decode(message)
                if message["message type"] == "ack":
                    print(f"Received ack from client at {client_port}, closing server at port {port}")
                    s.close()
                    return

    def welcome(self):
        welcome_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        welcome_socket.bind((self.host_ip, self.welcome_port))
        print("UDP server up and listening")
        while True:
            try:
                message, client_address = welcome_socket.recvfrom(1024)
                message = decode(message)
                if message["message type"] == "syn":
                    new_port = self.get_new_port()
                    new_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                    new_socket.bind((self.host_ip, new_port))
                    print(f"Received SYN from {client_address}, sending SYN/ACK, new port created at {new_port}")
                    message = encode("syn/ack", self.welcome_port, client_address[1], str(new_port))
                    welcome_socket.sendto(message, client_address)
                    message = welcome_socket.recv(1024)
                    message = decode(message)
                    if message["message type"] == "ack":

                        new_client_port = int(message["data"])
                        self.new_socket(new_socket, new_port, new_client_port)
                        """
                        start_new_thread(self.new_socket, (new_socket, new_port, new_client_port))
                        print_lock.acquire()
                        new_thread = threading.Thread(target=self.new_socket, args=)
                        new_thread.start()
                        """
            except KeyboardInterrupt:
                for s in self.sockets_used:
                    s.close()
                welcome_socket.close()
                break

    def run(self):
        self.welcome()
        """
        print_lock.acquire()
        start_new_thread(self.welcome, ())
        
        welcome = threading.Thread(target=self.welcome, args=())
        welcome.start()
        """


def main():
    args = sys.argv
    ip = args[1]
    server_welcome_port = int(args[2])
    server = Server(ip, server_welcome_port)
    server.run()


main()