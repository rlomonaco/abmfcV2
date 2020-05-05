import socket
import zmq

class Subscriber:

    def __init__(self, host, port):

        # # Connect a TCP/IP socket to serialisemonitor.cpp from rcssserver
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = (host, port)
        self.sock.connect(address)

    def recv(self):

        return self.sock.recv(1024).decode("utf-8")

class Publisher:

    def __init__(self, port):

        # connect zmq to publish to move_commands.py
        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind("tcp://*:"+str(port))

    def send(self, msg):

    	self.publisher.send_string(msg)