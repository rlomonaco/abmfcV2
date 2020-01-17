import socket
import zmq
import numpy as np
import datetime


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
        self.publisher_move.bind("tcp://*:7777") # 5555
        self.publisher_move.setsockopt(zmq.SNDHWM, 10)

        # connect zmq to publish to chain_commands.py
        context = zmq.Context()
        self.publisher_chain = context.socket(zmq.PUB)
        self.publisher_chain.bind("tcp://*:9999") #6666

        self.shows = []
        self.show = ""

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
            if "show" in msg:
                break

        # self.shows.append(message)
        # self.show = message

        return message

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

    def decode_msg(self):
        '''
        decode message for reinforcement learning
        '''




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
    msg1 = "6,1,-50,0" # player_num, action(pass), x, y

    while len(message) > 0:
        start = datetime.datetime.now()
        message = s.receive_msg()
        print(datetime.datetime.now() - start)
        # print(message)
        # print("shit")
        s.pub_move_msg(msg0)
        s.pub_chain_msg(msg1)
    print('done')

