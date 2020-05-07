from parser import Parser
from action_chain import Action_Chain
import numpy as np
from dominant_region import dom_reg_grid
from object import Shoot, Dribble, Pass, Ball, Player
from utils import caldist, passing_scores, shooting_scores, dribble_grid, find_nearest
import cv2


# ==============================================================================
# define class world_model
# ==============================================================================

class World_Model:


    def __init__ (self, host, port, move_port, chain_port):
        '''
        initialise parser and variables
        '''
        self.p = Parser(host, port, move_port, chain_port)
        self.op_goal = np.array([52.5, 0])
        self.players = []

        # self.update()

    def update(self):
        '''
        update world_model values from parsed message
        '''
        show, scores, ball, last_kick, players_table = self.p.parse_msg()
        # if len(players_table) == 22:
            # print(players[:,2:4])
        self.show = show
        self.scores = scores
        self.ball = Ball(ball)
        self.last_kick = last_kick

        ball_dist = np.array([caldist(players_table[i,2:4], self.ball.pos) for i in range(22)])

        self.ball_holder = int(np.argwhere(ball_dist == ball_dist.min())[0])

        self.goal_dist = np.array([caldist(players_table[i,2:4], self.op_goal) for i in range(22)])
        self.opp_dist = np.array([caldist(players_table[j, 2:4], players_table[self.ball_holder, 2:4]) for j in range(11,22)])

        self.players = [Player(i, players_table[i,:], self.ball_holder, ball_dist[i], self.goal_dist[i]) for i in range(22)]

        region, team_region, opp_region, max_points = dom_reg_grid(players_table[:11,2:4],
                            players_table[11:,2:4],players_table[:11,4:6],
                            players_table[11:,4:6], ball_dist)
        self.pass_scores = passing_scores(self.ball.pos, max_points, region)
        self.max_points = max_points
        grid_cost = self.dribble_gen(region)

        self.shot_scores = shooting_scores(players_table[:,2:4].copy())
        self.shoots = [Shoot(i, players_table[i,2:4], self.shot_scores[i]) for i in range(11)]
        self.passes = [Pass(self.ball_holder, self.ball.pos, i, players_table[i,2:4], max_points[i], self.pass_scores[i]) for i in range(1,11)]
        self.dribbles = [Dribble(self.ball_holder, self.ball.pos, grid_cost[i],i) for i in range(9)]


        self.ac = Action_Chain(self.scores, self.players, self.shoots, self.passes, self.dribbles)
        chain_array = self.ac.act_gen()
        self.chain(chain_array)



    def dribble_gen(self, region):
        '''
        generate action class dribble from grid cost
        '''
        loc = self.players[self.ball_holder].pos
        pos = loc.copy()
        pos[0] = (pos[0] + 50)
        pos[1] = (pos[1] + 35)
        pos = pos.astype(int)

        coord = np.array([pos.copy()[1], pos.copy()[0]])
        dribble_cost = dribble_grid(region, 15, coord.copy())

        row_n = 3
        col_n = 3
        grid = cv2.resize(dribble_cost, dsize=(row_n, col_n), interpolation=cv2.INTER_CUBIC).astype(int)
        return np.reshape(grid, np.prod(grid.shape))



    def move(self, array):
        '''
        send array of tagret positions for movements
        '''
        self.p.send_moves(array)

    def chain(self, array):
        '''
        send list/array of the decided action command
        '''
        # print(array)
        self.p.send_chains(array)















    def actions(self):

        which_point = self.max_points.copy()

        which_point[:, 0][self.pass_scores < 0] = -100

        target = np.argmax(which_point[:, 0]) + 1  # pass score doesn't include keeper, prevent back pass

        # target = np.argmax(pass_scores) + 1 # pass score doesn't include keeper, prevent back pass
        x = int(self.players[target].pos[0])
        y = int(self.players[target].pos[1])

        min_shot_dist = 15

        self.shot_scores[self.goal_dist[:11] > min_shot_dist] = 0
        shooting_man = int(np.argwhere(self.shot_scores == self.shot_scores.max())[0])
        num = 1
        if self.goal_dist[self.ball_holder] < min_shot_dist:
            return [self.ball_holder, 3, self.dribbles[num].target_point[0], self.dribbles[num].target_point[1],
                    self.ball_holder]
        return [self.ball_holder, 1, self.dribbles[num].target_point[0], self.dribbles[num].target_point[1], self.ball_holder]








