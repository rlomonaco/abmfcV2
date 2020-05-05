import matplotlib.pyplot as plt
import numpy as np

def caldist(p1, p2):
    '''
    calculate distance between two points
    '''
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def dom_reg_grid(team1p, team2p, team1v, team2v, ball_dist):

    team_region = np.zeros([71,101])
    opp_region = np.zeros([71,101])
    max_point = []
    for i in range(len(team1p)):
        pos_region = points_to_circle(team1p[i], team1v[i], ball_dist[i], factor=5, sigma=1/4)
        neg_region = points_to_circle(team2p[i], team2v[i], ball_dist[i+11], factor=5, sigma=1/4)
        team_region[pos_region>team_region] = pos_region[pos_region>team_region]
        opp_region[neg_region>opp_region] = neg_region[neg_region>opp_region]

        max_point.append(list(np.argwhere(pos_region==pos_region.max())[0]))
    # plt.imshow(region)
    region = np.zeros([71,101])
    region[team_region>opp_region] = team_region[team_region>opp_region]
    region[opp_region>=team_region] = -opp_region[opp_region>=team_region]
    return region, team_region, opp_region, np.array(max_point)

def paste_slices(tup):
    pos, w, max_w = tup
    wall_min = max(pos, 0)
    wall_max = min(pos + w, max_w)
    block_min = -min(pos, 0)
    block_max = max_w - max(pos + w, max_w)
    block_max = block_max if block_max != 0 else None

    return slice(wall_min, wall_max), slice(block_min, block_max)

def paste(wall, block, loc):
    loc_zip = zip(loc, block.shape, wall.shape)
    wall_slices, block_slices = zip(*map(paste_slices, loc_zip))
    wall[wall_slices] = block[block_slices]

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

def points_to_circle(coord, vel, ball_d, factor=None, sigma=None):

    x, y = np.meshgrid(np.linspace(-20,20,41), np.linspace(-20,20,41))
    x = x-vel[0]*ball_d*0.2
    y = y-vel[1]*ball_d*0.2
    d = np.sqrt(x * x + y * y)
    sigma, mu = ball_d*sigma, 0
    g = np.exp(-((d - mu) ** 2 / (2.0 * sigma ** 2)))


    output = np.zeros([71,101])
    loc_y = int(coord[1]+35-(g.shape[1]-1)/2)
    loc_x = int(coord[0]+50-(g.shape[0]-1)/2)
    paste(output, g*factor, (loc_y, loc_x))
    return output

# def gen_rand_val_for_testing():
#     n_points = 22

#     width = (-50, 50)
#     height = (-34, 34)
#     vmax = 0.1

#     a = 1

#     team1p = np.vstack([[np.random.uniform(width[0], width[1]),
#                          np.random.uniform(height[0], height[1])] for i in range(11)])
#     ball = team1p[9]
#     team2p = np.vstack([[np.random.uniform(width[0], width[1]),
#                          np.random.uniform(height[0], height[1])] for i in range(11)])
#     ball_dist = [caldist(team1p[i], ball) for i in range(11)]
#     ball_dist.extend([caldist(team2p[i], ball) for i in range(11)])
#     ball_dist = np.array(ball_dist)
#     team1v = np.vstack([[np.random.uniform(-vmax, vmax),
#                          np.random.uniform(-vmax, vmax)] for i in range(11)])
#     team2v = np.vstack([[np.random.uniform(-vmax, vmax),
#                          np.random.uniform(-vmax, vmax)] for i in range(11)])


# print('done')