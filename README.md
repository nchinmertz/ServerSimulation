This project simulates a TCP server-client connection using UDP sockets. Both the client and server initialize with a welcoming socket which facilitates a three-way handshake to establish a connection. Once estalished, communication is transferred to the two new sockets, the numbers of which are exchanged during the handshake.

The client and server will engage in a ping-pong message exchange until a keyboaard interruption is detected on either side. When this happends, a `fin` message is sent from the side where the keyboard interruption occurred. Both new sockets are then closed, along with the client welcome socket. The server welcome socket is also closed if the keyboard interuption occurs on the server side. 

While a second client can be initiated, the server is constrained to communcation with only one client at a time. Upon contact from a second client, the server will continue to use the same welcome socket

To execute:
1. Run the server: `python3 server.py ip_address port_number`
2. Run the client: `python3 client.py ip_address port_number`

Replace `ip_address` and `port_number` with the appropriate values
