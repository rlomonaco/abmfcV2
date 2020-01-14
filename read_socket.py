import socket
import zmq


class mysocket:

    def __init__(self):
        # # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 8889)
        self.sock.connect(server_address)

        # context = zmq.Context()
        # self.subscriber = context.socket(zmq.SUB)
        # self.subscriber.bind("tcp://*:8889")
        # self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        # connect zmq socket
        # context = zmq.Context()
        # self.socket = context.socket(zmq.PUB)
        # socket_address = "tcp://localhost:5555"
        # self.socket.connect(socket_address)

    def receive_msg(self):

        message = self.sock.recv(1024).decode("utf-8")

        # Read envelope with address
        # message = self.subscriber.recv_string()
        print(message)
        return message

    def send_msg(self, msg):
        # message argument has to be in byte

        self.socket.send_string(msg)


if __name__ == "__main__":

    s = mysocket()
    msg = " "
    # msg = "-50,-40,-30,-20,-10,-50,-40,-30,-20,-10,0"
    while len(msg) > 0:
        message = s.receive_msg()
        # s.send_msg(msg)
    print('done')

