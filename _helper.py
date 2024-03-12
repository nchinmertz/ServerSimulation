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