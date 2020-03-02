import numpy as np
from dominant_region import dom_reg_grid
from bresenham import bresenham
# ==============================================================================
# define functions
# ==============================================================================
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

    def actions(self, ball):
        self.ball = ball
        ball_dist = np.array([caldist(self.players[i, 2:4], self.ball) for i in range(22)])
        region, max_points = dom_reg_grid(self.team_players[:,2:4], self.opp_players[:,2:4],self.team_players[:,4:6], self.opp_players[:,4:6], ball_dist)

        # print(region)

        team_pos = self.team_players[:,2:4]
        pass_scores = []
        for j in range(1, 11):
            pixels = np.array(list(bresenham(int(ball[0]), int(max_points[j][0]), int(ball[1]), int(max_points[j][1]))))
            pass_scores.append(np.sum(region[pixels[:, 0], pixels[:, 1]]))
        pass_scores = np.array(pass_scores)
        try:
            region[int(ball[1]+35), int(ball[0]+50)] = np.nan
        except IndexError:
            print('goal')

    # ================================= save region matrix for analysis =================================
    #     save_num = 0
    #
    #     try:
    #         regions = np.load(f'regions_{save_num}.npy')
    #         player_pos = np.load(f'player_pos_{save_num}.npy')
    #         regions = np.append(regions, region.reshape(71,101,1), axis=2)
    #         player_pos = np.append(player_pos, self.players.reshape(self.players.shape+(1,)), axis=2)
    #         np.save(f'regions_{save_num}.npy', regions)
    #         np.save(f'player_pos_{save_num}.npy', player_pos)
    #     except:
    #         np.save(f'regions_{save_num}.npy', region.reshape(71,101,1))
    #         np.save(f'player_pos_{save_num}.npy', self.players.reshape(22,7,1))
    # ===================================================================================================
        # x = np.where(region==region.max())[0][0]-50
        # y = np.where(region==region.max())[1][0]-35
        # target = np.argmin([caldist(self.team_players[j, 2:4], [x,y]) for j in range(11)])
    # ===================================================================================================
        opp_distance = [caldist(self.opp_players[j, 2:4], self.players[self.num, 2:4]) for j in range(11)]
        target = np.argmax(pass_scores) + 1
        x = max_points[target][0]-50
        y = max_points[target][1]-35

        if caldist(np.array([50,0]), self.ball) < 10:
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







