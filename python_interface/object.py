import numpy as np
from utils import caldist
# ==============================================================================
# define variables
# ==============================================================================
row = np.arange(-5, 5 + 1, 5)
X = np.meshgrid(row, row)[0]
Y = np.meshgrid(row, row)[0].T
x = np.reshape(X, np.prod(X.shape))
y = np.reshape(Y, np.prod(Y.shape))
goal = np.array([52.5,0])

# ==============================================================================
# define action object classes
# ==============================================================================

class Dribble:

    def __init__(self, unum, coord, grid_cost, grid_unum, force=1):

        self.cat = 1
        self.unum = unum
        self.target_unum = unum
        self.coord = coord
        self.grid_pos = np.array([x[grid_unum], y[grid_unum]])
        self.target_point = coord + self.grid_pos*force
        self.goal_dist = caldist(self.target_point, goal)
        self.score = grid_cost

class Pass:

    def __init__(self, unum, coord, target_unum, target_point, through_point, pass_scores):

        self.cat = 2
        self.unum = unum
        self.coord = coord
        self.target_point = target_point

        self.target_unum = target_unum
        self.through_point = through_point

        self.goal_dist = caldist(self.target_point, goal)
        self.score = pass_scores

class Shoot:

    def __init__(self, unum, coord, shot_scores):

        self.cat = 3
        self.unum = unum
        self.target_unum = unum
        min_shooting_dist = 12
        if caldist(coord, goal) < 12:
            self.score = shot_scores
        else:
            self.score = -10

        self.target_point = goal


# ==============================================================================
# define game object classes
# ==============================================================================

class Ball:

    def __init__(self, ball):

        self.pos = ball[:2]
        self.vel = ball[2:]


class Player:

    def __init__(self, unum, players, ball_holder, ball_dist, goal_dist):

        self.unum = unum
        self.pos = players[2:4]
        self.vel = players[4:6]
        self.kick_count = players[6]
        self.stam = players[7]
        self.stam_cap = players[8]

        self.ball_dist = ball_dist
        self.goal_dist = goal_dist
        if ball_holder == unum:
            self.holder = True
        else:
            self.holder = False
