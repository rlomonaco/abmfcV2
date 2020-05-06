from mysock import Subscriber, Publisher
import numpy as np

a = [[-49., 0.],
     [-25., -5.],
     [-25., 5.],
     [-25., -10.],
     [-25., 10.],
     [-25., 0.],
     [-15., -5.],
     [-15., 5.],
     [-15., -10.],
     [-15., 10.],
     [-15., 0.],
     [49., -0.],
     [25., 5.],
     [25., -5.],
     [25., 10.],
     [25., -10.],
     [25., 0],
     [15., 5.],
     [15., -5.],
     [15., 10.],
     [15., -10.],
     [15., -0.]]

class Parser:

    def __init__(self, host, port, move_port, chain_port):

        # initialise sockets
        self.sock = Subscriber(host, port)
        self.publish_move = Publisher(move_port)
        self.publish_chain = Publisher(chain_port)

        # initialise variables
        self.holder = 11
        self.scores = np.zeros(2)
        self.show = 0
        self.kickcount = np.zeros(22)
        self.ball = np.zeros(4)
        self.players = np.zeros([22,9])
        self.players[:, 2:4] += np.array(a)



    def portion_msg(self):

        message = ""
        msg = " "
        while len(msg)>0:

            msg = self.sock.recv()
            message += msg

            if "side: -1, num:11" in msg:
                break

        return message

    def parse_msg(self):
        '''
        show:0
        team_l:0
        team_r:0
        ball_x:0.000000, ball_y:0.000000, ball_vx:0.000000, ball_vy:0.000000
        side: 1, num:1, x:-49.000000, y:0.000000, vel_x:0.000000, vel_y:0.000000, kick_count:0,
            stamina, staminaCapacity
        '''
        message = self.portion_msg()
        lines = message.split('\n')
        # print(len(lines))
        if len(lines) == 26:
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
                pass
     
            self.holder = np.argwhere(self.players[:,-3]-self.kickcount > 0)
            # self.player_pos = self.players[:,2:4].copy()
            # self.player_vel = self.players[:,4:6].copy()
            # self.player_stam = self.players[:,7:].copy()
            self.kickcount = self.players[:,6].copy()

        return self.show, self.scores, self.ball.copy(), self.holder, self.players.copy()

    def format_move_message(self, array, on_off=False):
        '''
        format move commands to string message from array
        [x1 y1,x2 y2, ... ,xn yn]
        also add 0, or 1, at the start to switch between our control or their own control
        '''
        array = np.array(array)
        oned_array = np.reshape(array, np.prod(array.shape))
        deliminater = [' ', ',']
        message = ""

        for x, m in enumerate(oned_array):
            message += str(m)+deliminater[x%2]

        # return str(on_off) + "," + message[:-1]
        return "0,0,-50 0,-30 -25,-35 -7,-35 7,-30 25,-10 -25,-15 -5,-15 5,-10 25,5 -5,5 5"

    def format_chain_message(self, array, on_off=True):
        '''
        format chain commands to string message from array
        [player_num, action(pass), x, y, target]
        '''

        message = ""
        for a in array:
            message += str(a)+","
        # print(str(int(on_off)) + "," + message[:-1])
        return str(int(on_off)) + "," + message[:-1]
        # return "0,1,1,2,3,4"

    def send_moves(self, array):

        self.publish_move.send(self.format_move_message(array))

    def send_chains(self, array):

        self.publish_chain.send(self.format_chain_message(array))
