import numpy as np
from bresenham import bresenham

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


def paste_slices(tup):
    pos, w, max_w = tup
    wall_min = max(pos, 0)
    wall_max = min(pos + w, max_w)
    block_min = -min(pos, 0)
    block_max = max_w - max(pos + w, max_w)
    block_max = block_max if block_max != 0 else None

    return slice(wall_min, wall_max), slice(block_min, block_max)

def dribble_grid(wall, block_size, loc, cost=-100):
    loc -= int((block_size-1)/2)
    block = np.zeros([block_size,block_size])
    loc_zip = zip(loc, block.shape, wall.shape)
    wall_slices, block_slices = zip(*map(paste_slices, loc_zip))
    boundary = np.ones([block_size, block_size])*cost
    boundary[block_slices] = wall[wall_slices]

    return boundary
    # return wall_slices, block_slices

def find_nearest(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = np.abs(a - a0).argmin()
    return a.flat[idx]


def passing_scores(ball, max_points, region):
    '''
    calculate pixel cost of the pass
    '''
    # ball = ball + np.array([50,35])
    region[region>0] = 0
    pass_scores = []
    for j in range(0, 11):
        pixels = np.array(list(bresenham(int(ball[0]),
                                         int(max_points[j][0]), int(ball[1]), int(max_points[j][1]))))
        pass_scores.append(np.sum(region[pixels[:, 0], pixels[:, 1]]))
    pass_scores = np.array(pass_scores)

    return pass_scores

def shooting_scores(player_pos):

    scores = []
    for p in player_pos[:11,:]:
        scores.append(shade_length(p, player_pos[11,:]))
    return np.array(scores)


