import socket


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    @staticmethod
    def make_packet(packet_type, source, dest, data=""):
        line2str = ""
        if packet_type == "ack":
            line2str = "1000"
        elif packet_type == "syn":
            line2str = "0100"
        elif packet_type == "fin":
            line2str = "0010"
        elif packet_type == "pong":
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
        if int(message[32]) == 1:
            message_type = "ack"
        elif int(message[33]) == 1:
            message_type = "syn"
        elif int(message[34]) == 1:
            message_type = "fin"
        elif int(message[35]) == 1:
            message_type = "ping"
        elif int(message[35]) == 1 and int(message[32]) == 1:
            message_type = "syn/ack"
        return {"source": int(message[:16], 2), "dest": int(message[16:32], 2),
                "message type": message_type, "data": message[36:]}

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(10000)
        print("listening")
        try:
            message, client_address = self.socket.recvfrom(1024)
            print("message received")
            message = self.decode_message(message)
            if message["message type"] == "ping":
                print("Traverse Tree")
                # make and send packet

            elif message["message type"] == "fin":
                self.socket.close()
        except KeyboardInterrupt:
            self.socket.close()


def main():
    host = "192.168.0.136"
    port = 65432
    server = Server(host, port)
    server.run()


main()
