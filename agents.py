import numpy as np

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

        self.speeds = [caldist(self.players[i, 4:6], np.array([0,0])) for i in range(22)]

    def movement(self, players):
        self.players = players
        self.self = players[self.num, :]

        self.cal_distances()
        self.cal_speeds()

        if self.onball == self.num:
            target_pos = [0,0]

        elif self.onball < 11:
            target_pos = self.players[self.num,2:4]
        else:
            # target_player = min(range(len(self.distances)), key=self.distances.__getitem__) #get index of minimum value
            target_pos = self.players[self.focus+11,2:4]
            # print(target_pos)

        return target_pos

    def actions(self):

        if self.onball == self.num:

            angles = np.array([calangles(self.players[j, 2:4], self.players[self.num, 2:4]) for j in range(22)])
            index = np.argsort(angles)
            diff = np.diff(angles[index])
            diff = np.insert(diff, 0, abs(diff[-1]-diff[0]))
            diff = np.append(diff, diff[0])
            free = [diff[i] + diff[i + 1] for i in range(22)]
            sortfree = np.array(free)[np.argsort(index)]

            mostfree = min(range(len(sortfree[:11])), key=sortfree[0:11].__getitem__) #get index of minimum value

            return [self.num+1, 2, self.players[mostfree, 2],self.players[mostfree, 3]]
        else:
            return []






