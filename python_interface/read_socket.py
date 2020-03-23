import socket
import zmq
import numpy as np
from agents import Agents

# ==============================================================================
# class
# ==============================================================================
class mysocket:

    def __init__(self):
        '''
        initialise all server connections
        '''
        # # Connect a TCP/IP socket to serialisemonitor.cpp from rcssserver
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
        self.onball = -1
        self.show = -1
        self.kickcount = np.zeros(22)
        self.last_kick = -1
        self.actioned = False
        self.agents = []
        self.move_message = "-25 0,-25 -5,-25 5,-25 -10,-25 10,-15 0,-15 -5,-15 5,-15 -10,-15 10,15 -0"
        self.chain_message = "10,1,-50,0"


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

    def decode_msg(self, lines):
        '''
        decode message for reinforcement learning

        show:0
        team_l:0
        team_r:0
        ball_x:0.000000, ball_y:0.000000, ball_vx:0.000000, ball_vy:0.000000
        side: 1, num:1, x:-49.000000, y:0.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0,
            stamina, staminaCapacity
        side: 1, num:2, x:-25.000000, y:-5.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: 1, num:3, x:-25.000000, y:5.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: 1, num:4, x:-25.000000, y:-10.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: 1, num:5, x:-25.000000, y:10.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: 1, num:6, x:-25.000000, y:0.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: 1, num:7, x:-15.000000, y:-5.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: 1, num:8, x:-15.000000, y:5.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: 1, num:9, x:-15.000000, y:-10.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: 1, num:10, x:-15.000000, y:10.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: 1, num:11, x:-15.000000, y:0.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: -1, num:2, x:25.000000, y:5.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: -1, num:3, x:25.000000, y:-5.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: -1, num:4, x:25.000000, y:10.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: -1, num:5, x:25.000000, y:-10.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: -1, num:6, x:25.000000, y:-0.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: -1, num:7, x:15.000000, y:5.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: -1, num:8, x:15.000000, y:-5.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: -1, num:9, x:15.000000, y:10.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: -1, num:10, x:15.000000, y:-10.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        side: -1, num:11, x:15.000000, y:-0.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0
        '''

        try:
            self.show = int(lines[0].split(':')[-1])
            self.scores = np.array([int(lines[1].split(':')[-1]), int(lines[2].split(':')[-1])])
        except ValueError:
            print('score and show error')
        self.ball = np.array([np.float(val.split(':')[-1]) for val in lines[3].split(',')])
        try:
            players = []
            for i in range(4,len(lines)):
                player = [np.float(val.split(':')[-1]) for val in lines[i].split(',')]
                players.append(player)


            self.players = np.vstack(players)
        except ValueError:
            print('line error')

        if len(self.agents) < 1:
            self.agents = [Agents(self.players, self.ball, i) for i in range(11)]
            self.move_message = self.format_move_message(self.players[:11,2:4])
            # print(self.move_message)

        onball = np.argwhere(self.players[:,-3]-self.kickcount > 0)

        if len(onball) > 0:
            self.actioned = False
            for i in range(11):
                self.agents[i].onball = int(onball[0])
            self.onball = int(onball[0])



        self.kickcount = self.players[:,-3]
        # print(self.onball)

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
        also add 0, or 1, at the start to switch between our control or their own control
        '''

        oned_array = np.reshape(array, np.prod(array.shape))
        deliminater = [' ', ',']
        message = ""

        for x, m in enumerate(oned_array):
            message += str(m)+deliminater[x%2]

        return "1,"+message[:-1]

    def format_chain_message(self, array):
        '''
        format chain commands to string message from array
        [player_num, action(pass), x, y]
        '''
        if len(array)>0:
            message = ""
            for a in array:
                message += str(a)+","

            return message[:-1]
        return self.chain_message

    def commands(self, message):
        '''
        sometimes the messages don't have the full 26 lines due to probably error in the socket
        '''
        lines = message.split('\n')
        if len(lines) == 26:

            self.decode_msg(lines)
            move_array = []
            for i in range(11):
                move_array.append(self.agents[i].movement(self.players))

            self.move_message = self.format_move_message(np.vstack(move_array))

            if self.onball < 11 and self.show > 1:

                self.chain_message = self.format_chain_message(self.agents[self.onball].actions(self.ball))
                self.actioned = True
                self.last_kick = self.onball
        return self.move_message, self.chain_message

    def main(self):
        message = " "
        msg1 = self.chain_message

        while len(message) > 0:


            message = self.receive_msg()
            # print(message)
            msg0, msg1 = self.commands(message)

            self.pub_chain_msg(msg1)
            # self.pub_move_msg(msg0)

            # 0 and 1 added at the front from socket movement or abm movement
            # print(self.show)
            print(msg1)

            self.pub_move_msg("0,-50 0,-30 -25,-35 -7,-35 7,-30 25,-10 -25,-15 -5,-15 5,-10 25,5 -5,5 5")

if __name__ == "__main__":
    num = 0
    while num < 100:
        try:
            mysocket().main()
            print('done')
        except:
            print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
            num += 1
            pass
        # mysocket().main()

