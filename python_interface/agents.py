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
        pass_scores = []
        for j in range(1, 11):
            pixels = np.array(list(bresenham(int(ball[0]),
                                             int(max_points[j][0]), int(ball[1]), int(max_points[j][1]))))
            pass_scores.append(np.sum(region[pixels[:, 0], pixels[:, 1]]))
        pass_scores = np.array(pass_scores)

        # only used for saving npy regions
        # try:
        #     region[int(ball[1]+35), int(ball[0]+50)] = np.nan
        # except IndexError:
        #     print('goal')
        return pass_scores

    def actions(self, ball):
        self.ball = ball

        # calculate distances from self
        # should put in self.calc_distances
        ball_dist = np.array([caldist(self.players[i, 2:4], self.ball) for i in range(22)])
        opp_distance = np.array([caldist(self.opp_players[j, 2:4], self.players[self.num, 2:4]) for j in range(11)])
        goal_distance = np.array([caldist(self.opp_players[j, 2:4], np.array([52.5,0])) for j in range(11)])

        # get dominant regions
        region, team_region, opp_region, max_points = dom_reg_grid(
                        self.team_players[:,2:4], self.opp_players[:,2:4],self.team_players[:,4:6],
                        self.opp_players[:,4:6], ball_dist)

        # get scores
        shooting_scores = self.shooting_scores()
        pass_scores = self.passing_scores(ball, max_points, region)



        which_point = max_points.copy()
        which_point = np.delete(which_point,0, axis=0)
        print(which_point)
        print(pass_scores)
        which_point[:,0][pass_scores < 0] = -100


        target = np.argmax(which_point[:,0]) + 1 # pass score doesn't include keeper, prevent back pass

        # target = np.argmax(pass_scores) + 1 # pass score doesn't include keeper, prevent back pass

        x = max_points[target][0]-50
        y = max_points[target][1]-35

        min_shot_dist = 12

        shooting_scores[goal_distance>min_shot_dist] = 0
        shooting_man = int(np.argwhere(shooting_scores == shooting_scores.max())[0])

        if caldist(np.array([52.5,0]), self.ball) < min_shot_dist and shooting_man != self.num:
            print('square')
            x = max_points[shooting_man][0] - 50
            y = max_points[shooting_man][1] - 35
            return [self.num, 2, x, y, target]
        if caldist(np.array([52.5,0]), self.ball) < min_shot_dist:
            print('shoot')
            return [self.num, 3, 50, 0, target]
        elif np.max(pass_scores) <= 0 and np.min(opp_distance) > 5:
            print('dribble')
            return [self.num, 1, 50, 0, target]
        elif np.max(pass_scores) <= 0:
            print('hold')
            return [self.num, 0, 50, 0, target]
        else:
            print('pass')
            return [self.num, 2, x, y, target]

    def nodes(self, ball, region):

        self.ball = ball
        # self.moves = [str(i) for i in range(1,10)]#1 to 9 on the grid with 5 in the middle

        grid = cv2.resize(region, dsize=(self.col, self.row), interpolation=cv2.INTER_CUBIC).astype(int)
        pos = self.team_players[self.num, 2:4]
        pos[0] = int((pos[0]+50)/5)
        pos[1] = int((pos[1]+35)/5)

        moves = grid[tuple(pos)]
