import socket
import zmq
import numpy as np


class mysocket:

    def __init__(self):
        '''
        initialise all server connections
        '''
        # Connect a TCP/IP socket to serialisemonitor.cpp from rcssserver
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 8889)
        self.sock.connect(server_address)

        # connect zmq to publish to move_commands.py
        context = zmq.Context()
        self.publisher_move = context.socket(zmq.PUB)
        self.publisher_move.bind("tcp://*:7777")

        # connect zmq to publish to move_commands.py
        context = zmq.Context()
        self.publisher_chain = context.socket(zmq.PUB)
        self.publisher_chain.bind("tcp://*:6666")

        # self.messages = []
        # self.message = ""

        self.show = 0

    def receive_msg(self):
        '''
        receive messages
        '''
        message = ""
        msg = " "
        while len(msg)>0:
            msg = self.sock.recv(1024).decode("utf-8")
            message += msg
            # print(message)
            if "side: -1, num:11" in msg:
                break

        # self.messages.append(message)
        # self.message = message

        return message

    def decode_msg(self, message):
        '''
        decode message for reinforcement learning
        '''



    def pub_move_msg(self, msg):
        '''
        send strings to socket with msg input
        '''

        self.publisher_move.send_string(msg)

    def pub_chain_msg(self, msg):
        '''
        send strings to socket with msg input
        '''

        self.publisher_chain.send_string(msg)

    def format_move_message(self, array):
        '''
        format move commands to string message from array
        [x1 y1,x2 y2, ... ,xn yn]
        '''

        oned_array = np.reshape(array, np.prod(array.shape))
        deliminater = [' ', ',']
        message = ""

        for x, m in enumerate(oned_array):
            message += str(m)+deliminater[x%2]

        return message[:-1]

    def format_chain_message(self, array):
        '''
        format chain commands to string message from array
        [player_num, action(pass), x, y]
        '''

        message = ""
        for a in array:
            message += str(a)+","

        return message[:-1]


if __name__ == "__main__":
    s = mysocket()
    message = " "
    msg0 = "-50 -25,-40 -25,-30 -25,-20 -25,-10 -25,-50 -25,-40 -25,-30 -25,-20 -25,-10 -25,0 -25"
    msg1 = "10,1,-50,0" # player_num, action(pass), x, y

    while len(message) > 0:
        message = s.receive_msg()
        s.decode_msg(message)
        # print(message+"\n\n\n\n\n\n\n")

        s.pub_chain_msg(msg1)
        s.pub_move_msg(msg0)
    print('done')

