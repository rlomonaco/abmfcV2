from parser import Parser
import numpy as np
from dominant_region import dom_reg_grid
from object import Shoot, Dribble, Pass, Ball, Player
from utils import caldist, passing_scores, shooting_scores, grid_moves, find_nearest
import cv2


# ==============================================================================
# define class world_model
# ==============================================================================

class World_Model():


    def __init__ (self, host, port, move_port, chain_port):

        self.p = Parser(host, port, move_port, chain_port)
        self.op_goal = np.array([52.5, 0])
        self.players = []

        # self.update()

    def update(self):

        show, scores, ball, holder, players_table = self.p.parse_msg()
        if len(players_table) == 22:
            # print(players[:,2:4])
            self.show = show
            self.scores = scores
            self.ball = Ball(ball)
            self.holder = holder

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
            # max_points += np.array([50,35])
            self.shot_scores = shooting_scores(players_table[:,2:4].copy())
            self.shoots = [Shoot(i, self.shot_scores[i]) for i in range(11)]
            self.passes = [Pass(self.ball_holder, self.ball.pos, i, players_table[i,2:4], max_points[i], self.pass_scores[i]) for i in range(1,11)]
            dribble = self.nodes(region)
            self.dribble = Dribble(self.ball_holder, self.ball.pos, dribble)

            chain_array = self.actions()
            self.chain(chain_array)



    def actions(self):

        which_point = self.max_points.copy()

        which_point[:, 0][self.pass_scores < 0] = -100

        target = np.argmax(which_point[:, 0]) + 1  # pass score doesn't include keeper, prevent back pass

        # target = np.argmax(pass_scores) + 1 # pass score doesn't include keeper, prevent back pass
        x = int(self.players[target].pos[0])
        y = int(self.players[target].pos[1])

        min_shot_dist = 12

        self.shot_scores[self.goal_dist[:11] > min_shot_dist] = 0
        shooting_man = int(np.argwhere(self.shot_scores == self.shot_scores.max())[0])

        if np.max(self.pass_scores) <= -5 and np.min(self.opp_dist) > 5:
        # print('dribble')
            return [self.ball_holder, 1, self.dribble.target_point[0], self.dribble.target_point[1], self.ball_holder]
        elif caldist(np.array([52.5, 0]), self.ball.pos) < min_shot_dist and shooting_man != self.ball_holder:
            # print('square')
            x = self.max_points[shooting_man][0] - 50
            y = self.max_points[shooting_man][1] - 35
            return [self.ball_holder, 2, x, y, target]
        elif caldist(np.array([52.5, 0]), self.ball.pos) < min_shot_dist:
            # print('shoot')
            return [self.ball_holder, 3, 50, 0, target]

        elif np.max(self.pass_scores) <= -5:
            # print('hold')
            return [self.ball_holder, 0, 50, 0, target]
        else:
            # print('pass')
            return [self.ball_holder, 2, x, y, target]

    def nodes(self, region):

        # self.moves = [str(i) for i in range(1,10)]#1 to 9 on the grid with 5 in the middle
        # players = np.load('/home/godfrey/abm-fc/python_interface/saved_heatmaps/player_pos_0.npy')
        row_n = 20
        col_n = 14
        grid = cv2.resize(region, dsize=(row_n, col_n), interpolation=cv2.INTER_CUBIC).astype(int)
        grid = -grid

        loc = self.players[self.ball_holder].pos
        pos = loc.copy()
        pos[0] = (pos[0] + 50) / 5
        pos[1] = (pos[1] + 35) / 5
        pos = pos.astype(int)
        # print(pos)

        row = np.meshgrid(np.arange(col_n), np.arange(row_n))[0].T
        col = np.meshgrid(np.arange(row_n), np.arange(col_n))[0]

        # filter_kernel = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 0]])

        coord = np.array([pos.copy()[1], pos.copy()[0]])
        dribble_col = grid_moves(col, 3, coord.copy())
        dribble_row = grid_moves(row, 3, coord.copy())

        grid[find_nearest(dribble_row, 7), find_nearest(dribble_col, 20)] += 100

        dribble_cost = grid_moves(grid, 3, coord.copy())
        try:
            max_dribble = tuple(np.argwhere(dribble_cost == dribble_cost.max())[0])
        except ValueError:
            max_dribble = (0, 0)

        x = (dribble_col * 5 - 50)[max_dribble] - self.players[self.ball_holder].pos[0]
        y = (dribble_row * 5 - 35)[max_dribble] - self.players[self.ball_holder].pos[1]

        return [int(loc[0] + x), int(loc[1] + y)]

    def move(self, array):

        self.p.send_moves(array)

    def chain(self, array):

        self.p.send_chains(array)










