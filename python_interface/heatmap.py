import numpy as np
import matplotlib.pyplot as plt
from bresenham import bresenham

file_num = 0
regions = np.load(f'regions_{file_num}.npy')
player_poss = np.load(f'player_pos_{file_num}.npy')
for i in range(regions.shape[2]):
    plt.figure()
    region = regions[:,:,i]
    player_pos = player_poss[:,:,i]
    plt.imshow(region)
    plt.scatter(player_pos[:11,2]+50, player_pos[:11,3]+35, c='r')
    plt.scatter(player_pos[11:, 2] + 50, player_pos[11:, 3] + 35, c='b')

    ball = np.argwhere(np.isnan(region))[0]
    team_pos = player_pos[:11,2:4]
    pass_scores = []
    for j in range(11):
        pixels = np.array(list(bresenham(ball[0], int(team_pos[j][0]), ball[1], int(team_pos[j][1]))))
        pass_scores.append(np.sum(region[pixels[:,0], pixels[:,1]]))

print('done')