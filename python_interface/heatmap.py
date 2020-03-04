import numpy as np
import matplotlib.pyplot as plt
from bresenham import bresenham
import os
file_dir = os.getcwd()+'/python_interface/saved_heatmaps/'

file_num = 0
regions = np.load(file_dir + f'regions_{file_num}.npy')
player_poss = np.load(file_dir + f'player_pos_{file_num}.npy')
for i in range(100,110):
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

import cv2
a = cv2.resize(region, dsize=(10, 7), interpolation=cv2.INTER_CUBIC)
a = a.astype(int)
a[a>=0] = -1
a[2:5, -1] = 10
a[3, -1] = 50
a[3, -2] = 10
x = (player_pos[:11,2]+50)/10
x = x.astype(int)
y = (player_pos[:11,3]+35)/10
y = y.astype(int)

for i in range(len(x)):
    plt.figure()
    b = a
    b[y[i], x[i]] = 0
    plt.imshow(b)

print('done')