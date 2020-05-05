from parser import Parser
import numpy as np
from dominant_region import dom_reg_grid
from object import *
import cv2


# ==============================================================================
# define class world_model
# ==============================================================================

class World_Model():


    def __init__ (self, host, port, move_port, chain_port):

        self.p = Parser(host, port, move_port, chain_port)
        self.players = []

        # self.update()

    def update(self):

        show, scores, ball, holder, players = self.p.parse_msg()
        if len(players) == 22:
            # print(players[:,2:4])
            self.show = show
            self.scores = scores
            self.ball = Ball(ball)
            self.holder = holder
            ball_dist = np.array([caldist(players[i,2:4], self.ball.pos) for i in range(22)])
            self.ball_holder = int(np.argwhere(ball_dist == ball_dist.min())[0])
            region, team_region, opp_region, max_points = dom_reg_grid(players[:11,2:4],
                                players[11:,2:4],players[:11,4:6],
                                players[11:,4:6], ball_dist)

            pass_scores = passing_scores(self.ball.pos, max_points, region)
            shot_scores = shooting_scores(players[:,2:4].copy())
            self.shoots = [Shoot(i, shot_scores[i]) for i in range(11)]
            self.passes = [Pass(self.ball_holder, self.ball.pos, i, players[i,2:4], max_points[i-1], pass_scores[i-1]) for i in range(1,11)]
            dribble = self.nodes(self.ball.pos, region)
            self.dribble = Dribble(self.ball_holder, self.ball.pos, dribble)
            self.players = [Player(i, players[i,:], holder, ball_dist[i]) for i in range(22)]

    def actions(self):

        which_point = max_points.copy()
        which_point = np.delete(which_point, 0, axis=0)
        # print(which_point)
        # print(self.pass_scores)
        which_point[:, 0][self.pass_scores < 0] = -100

        target = np.argmax(which_point[:, 0]) + 1  # pass score doesn't include keeper, prevent back pass

        # target = np.argmax(pass_scores) + 1 # pass score doesn't include keeper, prevent back pass

        x = max_points[target][0] - 50
        y = max_points[target][1] - 35

        min_shot_dist = 12

        shooting_scores[goal_distance > min_shot_dist] = 0
        shooting_man = int(np.argwhere(shooting_scores == shooting_scores.max())[0])


        if caldist(np.array([52.5, 0]), self.ball) < min_shot_dist and shooting_man != self.num:
            # print('square')
            x = max_points[shooting_man][0] - 50
            y = max_points[shooting_man][1] - 35
            return [self.num, 2, x, y, target]
        if caldist(np.array([52.5, 0]), self.ball) < min_shot_dist:
            # print('shoot')
            return [self.num, 3, 50, 0, target]
        elif np.max(self.pass_scores) <= -5 and np.min(opp_distance) > 5:
            # print('dribble')
            return [self.num, 1, dribble[0], dribble[1], self.num]
        elif np.max(self.pass_scores) <= -5:
            # print('hold')
            return [self.num, 0, 50, 0, target]
        else:
            # print('pass')
            return [self.num, 2, x, y, target]

    def nodes(self, ball, region):

        # self.moves = [str(i) for i in range(1,10)]#1 to 9 on the grid with 5 in the middle
        players = np.load('/home/godfrey/abm-fc/python_interface/saved_heatmaps/player_pos_0.npy')
        row_n = 20
        col_n = 14
        grid = cv2.resize(region, dsize=(row_n, col_n), interpolation=cv2.INTER_CUBIC).astype(int)
        grid = -grid
        loc = self.players[self.ball_holder, 2:4].copy()
        pos = loc.copy()
        pos[0] = (pos[0] + 50) / 5
        pos[1] = (pos[1] + 35) / 5
        pos = pos.astype(int)
        # print(pos)

        row = np.meshgrid(np.arange(col_n), np.arange(row_n))[0].T
        col = np.meshgrid(np.arange(row_n), np.arange(col_n))[0]

        filter_kernel = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 0]])

        coord = np.array([pos.copy()[1], pos.copy()[0]])
        dribble_col = grid_moves(col, 3, coord.copy())
        dribble_row = grid_moves(row, 3, coord.copy())
        # print(pos)
        # print(grid)
        # print(dribble_col)
        # print(dribble_row)

        grid[find_nearest(dribble_row, 7), find_nearest(dribble_col, 20)] += 100

        dribble_cost = grid_moves(grid, 3, coord.copy())
        # print(dribble_cost)
        try:
            max_dribble = tuple(np.argwhere(dribble_cost == dribble_cost.max())[0])
        except ValueError:
            max_dribble = (0, 0)
        # print(max_dribble)
        # print((dribble_col*5-50)[max_dribble])
        x = (dribble_col * 5 - 50)[max_dribble] - self.players[self.ball_holder, 2]
        y = (dribble_row * 5 - 35)[max_dribble] - self.players[self.ball_holder, 3]
        # print(x,y)
        return (int(loc[0] + x), int(loc[1] + y))

    def move(self, array):

        self.p.send_moves(array)

    def chain(self, array):

        self.p.send_chains(array)










