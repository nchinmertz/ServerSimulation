import socket
import time


class Client:
    def __init__(self, host, port, website):
        self.host = host
        self.port = 65431 # random
        self.welcome_port = port
        self.website_name = website
        self.request = ""

    @staticmethod
    def make_packet(packet_type, source, dest, data=""):
        line2str = ""
        if packet_type == "ack":
            line2str = "1000"
        elif packet_type == "syn":
            line2str = "0100"
        elif packet_type == "fin":
            line2str = "0010"
        elif packet_type == "ping":
            line2str = "0001"
        elif packet_type == "syn/ack":
            line2str = "1001"
        elif packet_type is None:
            line2str = "0000"
        header = '{0:016b}'.format(source) + '{0:016b}'.format(dest) + line2str + str(data)
        return header.encode()

    @staticmethod
    def decode_message(message):
        message = message.decode()
        message_type = ""
        if int(message[35]) == 1 and int(message[32]) == 1:
            message_type = "syn/ack"
        elif int(message[33]) == 1:
            message_type = "syn"
        elif int(message[34]) == 1:
            message_type = "fin"
        elif int(message[35]) == 1:
            message_type = "pong"
        elif int(message[32]) == 1:
            message_type = "ack"
        return {"source": int(message[:16], 2), "dest": int(message[16:32], 2), "message type": message_type,
                "data": message[36:]}

    def tcp_connect(self, ip_address):
        message = f"GET / HTTP/1.1\r\nHost:www.{self.website_name}\r\n\r\n".encode()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10000)
        try:
            s.connect((ip_address, 80))
            s.sendto(message, (ip_address, 80))
            response = s.recvfrom(512)
            response = repr(response)
        except socket.timeout:
            return 0, 0
        with open(f"{self.website_name[:-4]}.html", "w") as file:
            file.write(response)

    def run(self):
        message = self.make_packet("ping", self.port, self.welcome_port, self.website_name)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        time.sleep(3)
        s.sendto(message, (self.host, self.welcome_port))
        print("Message sent")
        s.settimeout(10000)
        try:
            message, server_address = s.recvfrom(1024)
            message = self.decode_message(message)
            if message["message type"] == "pong":
                ip_address = message["data"]
                print("Make TCP connection")
                # self.tcp_connect(ip_address)
        except socket.timeout:
            s.close()


def main():
    host = "192.168.0.136"
    welcome_port = 65432
    website = "tmz.com"
    client = Client(host, welcome_port, website)
    client.run()


main()