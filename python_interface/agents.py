import numpy as np
from dominant_region import dom_reg_grid
from bresenham import bresenham
from graph import Graph
import cv2

# ==============================================================================
# define functions
# ==============================================================================
def shade_length(player_p, goalie_p):
    '''
    calculate shooting openess, need revision to check maths
    '''
    top_post = np.array([52.5, -6.5])
    bottom_post = np.array([52.5, 6.5])
    goalie_size = 1
    x = abs(player_p[0] - goalie_p[0])
    y = abs(player_p[1] - goalie_p[1])
    z = np.sqrt(x**2 + y**2)
    a = np.arctan(y/x)
    c = np.arcsin(goalie_size/z)
    x1 = top_post[0] - player_p[0]
    theta1 = a-c
    y1 = x1*np.tan(theta1)
    theta2 = a+c
    y2 = x1*np.tan(theta2)
    unshaded = (player_p[1]+y2-bottom_post[1]) + (top_post[1]- player_p[1]-y1)

    return abs(unshaded)/13

def pass_obstruct(ball_p, opp_p):
    '''
    find obstructed pass
    '''


def caldist(p1, p2):
    '''
    calculate distance between two points
    '''
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def calangles(p1, p2):
    '''
    calculate angle between two points
    '''
    return np.arctan2(p1[0]-p2[0], p1[1]-p1[1])


def paste_slices(tup):
    pos, w, max_w = tup
    wall_min = max(pos, 0)
    wall_max = min(pos + w, max_w)
    block_min = -min(pos, 0)
    block_max = max_w - max(pos + w, max_w)
    block_max = block_max if block_max != 0 else None

    return slice(wall_min, wall_max), slice(block_min, block_max)

def grid_moves(wall, block_size, loc):
    loc -= int((block_size-1)/2)
    block = np.zeros([block_size,block_size])
    loc_zip = zip(loc, block.shape, wall.shape)
    wall_slices, block_slices = zip(*map(paste_slices, loc_zip))
    return wall[wall_slices]

def find_nearest(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = np.abs(a - a0).argmin()
    return a.flat[idx]

class Agents:

    def __init__(self, players, ball, index):

        self.num = index
        self.players = players
        self.ball = ball
        self.onball = -1
        self.self = players[index, :]
        focus = [1,11,11,10,9,7,8,6,5,4,3]
        self.focus = focus[index]-1


    def cal_distances(self):

        self.distances = [caldist(self.players[j, 2:4], self.players[self.num, 2:4]) for j in range(22)]

    def cal_speeds(self):
        # ally and enemy spped
        self.team_speeds = [caldist(self.team_players[i, 4:6], np.array([0,0])) for i in range(11)]
        self.opp_speeds = [caldist(self.opp_players[i, 4:6], np.array([0, 0])) for i in range(11)]

    def movement(self, players):
        self.players = players
        self.team_players = players[:11]
        self.opp_players = players[11:]
        self.self = players[self.num, :]

        self.cal_distances()
        self.cal_speeds()

        if self.onball == self.num:
            target_pos = [0,0]

        elif self.onball < 11:
            target_pos = self.players[self.num,2:4]
        else:
            target_pos = self.players[self.focus+11,2:4]

        return target_pos

    def shooting_scores(self):

        scores = []
        for p in self.team_players[:,2:4]:
            scores.append(shade_length(p, self.opp_players[0,2:4]))
        return np.array(scores)

    def passing_scores(self, ball, max_points, region):
        '''
        calculate pixel cost of the pass
        '''
        region[region>0] = 0
        pass_scores = []
        for j in range(1, 11):
            pixels = np.array(list(bresenham(int(ball[0]),
                                             int(max_points[j][0]), int(ball[1]), int(max_points[j][1]))))
            pass_scores.append(np.sum(region[pixels[:, 0], pixels[:, 1]]))
        pass_scores = np.array(pass_scores)

        return pass_scores

    def actions(self, ball):
        self.ball = ball
        # calculate distances from self
        # should put in self.calc_distances
        self.ball_dist = np.array([caldist(self.players[i, 2:4], self.ball) for i in range(22)])
        opp_distance = np.array([caldist(self.opp_players[j, 2:4], self.players[self.num, 2:4]) for j in range(11)])
        goal_distance = np.array([caldist(self.opp_players[j, 2:4], np.array([52.5,0])) for j in range(11)])

        # get dominant regions
        region, team_region, opp_region, max_points = dom_reg_grid(
                        self.team_players[:,2:4], self.opp_players[:,2:4],self.team_players[:,4:6],
                        self.opp_players[:,4:6], self.ball_dist)

        # get scores
        shooting_scores = self.shooting_scores()
        self.pass_scores = self.passing_scores(ball, max_points, region.copy())

        dribble = self.nodes(ball, region)

        which_point = max_points.copy()
        which_point = np.delete(which_point,0, axis=0)
        # print(which_point)
        # print(self.pass_scores)
        which_point[:,0][self.pass_scores < 0] = -100


        target = np.argmax(which_point[:,0]) + 1 # pass score doesn't include keeper, prevent back pass

        # target = np.argmax(pass_scores) + 1 # pass score doesn't include keeper, prevent back pass

        x = max_points[target][0]-50
        y = max_points[target][1]-35

        min_shot_dist = 12

        shooting_scores[goal_distance>min_shot_dist] = 0
        shooting_man = int(np.argwhere(shooting_scores == shooting_scores.max())[0])
        return [1, self.num+1, 1, dribble[0], dribble[1], target]
        #
        # if caldist(np.array([52.5,0]), self.ball) < min_shot_dist and shooting_man != self.num:
        #     print('square')
        #     x = max_points[shooting_man][0] - 50
        #     y = max_points[shooting_man][1] - 35
        #     return [self.num, 2, x, y, target]
        # if caldist(np.array([52.5,0]), self.ball) < min_shot_dist:
        #     print('shoot')
        #     return [self.num, 3, 50, 0, target]
        # elif np.max(self.pass_scores) <= -5 and np.min(opp_distance) > 5:
        #     print('dribble')
        #     return [self.num, 1, dribble[0], dribble[1], target]
        # elif np.max(self.pass_scores) <= -5:
        #     print('hold')
        #     return [self.num, 0, 50, 0, target]
        # else:
        #     print('pass')
        #     return [self.num, 2, x, y, target]

    def nodes(self, ball, region):

        # self.moves = [str(i) for i in range(1,10)]#1 to 9 on the grid with 5 in the middle
        players = np.load('/home/godfrey/abm-fc/python_interface/saved_heatmaps/player_pos_0.npy')
        row_n = 20
        col_n = 14
        grid = cv2.resize(region, dsize=(row_n, col_n), interpolation=cv2.INTER_CUBIC).astype(int)
        grid = -grid
        loc = self.team_players[self.num, 2:4].copy()
        pos = loc.copy()
        pos[0] = (pos[0]+50)/5
        pos[1] = (pos[1]+35)/5
        pos = pos.astype(int)
        # print(pos)

        row = np.meshgrid(np.arange(col_n), np.arange(row_n))[0].T
        col = np.meshgrid(np.arange(row_n),np.arange(col_n))[0]

        filter_kernel = np.array([[0,0,0],[0,0,1],[0,0,0]])

        coord = np.array([pos.copy()[1],pos.copy()[0]])
        dribble_col = grid_moves(col, 3, coord.copy())
        dribble_row = grid_moves(row, 3, coord.copy())
        # print(pos)
        # print(grid)
        # print(dribble_col)
        # print(dribble_row)

        grid[find_nearest(dribble_row,7), find_nearest(dribble_col, 20)] +=100

        dribble_cost = grid_moves(grid, 3, coord.copy())
        print(dribble_cost)
        try:
            max_dribble = tuple(np.argwhere(dribble_cost == dribble_cost.max())[0])
        except ValueError:
            max_dribble = (0,0)
        print(max_dribble)
        # print((dribble_col*5-50)[max_dribble])
        x = (dribble_col*5-50)[max_dribble]-self.team_players[self.num, 2]
        y = (dribble_row*5-35)[max_dribble]-self.team_players[self.num, 3]
        print(x,y)
        return (int(loc[0]+x), int(loc[1]+y))

        # print(self.pass_scores)



