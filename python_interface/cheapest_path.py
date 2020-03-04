import numpy as np
import matplotlib.pyplot as plt
from bresenham import bresenham
import os
import cv2

def view(region, player_pos):
    plt.figure()
    plt.imshow(region)
    plt.scatter(player_pos[:11,2]+50, player_pos[:11,3]+35, c='r')
    plt.scatter(player_pos[11:, 2] + 50, player_pos[11:, 3] + 35, c='b')

def gen_input(opp_regions, player_poss):
    input_data = []
    for num in range(opp_regions.shape[2]):
        opp_region = opp_regions[:,:,num]
        player_pos = player_poss[:,:,num]

        # view(opp_region, player_pos)

        a = cv2.resize(opp_region, dsize=(10, 7), interpolation=cv2.INTER_CUBIC)
        a = -a.astype(int)
        a[a>=0] = -1
        a[2:5, -1] = 10
        a[3, -1] = 50
        a[3, -2] = 10
        x = (player_pos[:11,2]+50)/10
        x = x.astype(int)
        y = (player_pos[:11,3]+35)/10
        y = y.astype(int)

        for i in range(len(x)):
            # plt.figure()
            b = a.copy()
            b[y[i], x[i]] = 0
            input_data.append(b)

    return input_data

file_dir = os.getcwd()+'/saved_heatmaps/'
file_num = 0

regions = np.load(file_dir + f'regions_{file_num}.npy')
team_regions = np.load(file_dir + f'team_regions_{file_num}.npy')
opp_regions = np.load(file_dir + f'opp_regions_{file_num}.npy')
player_poss = np.load(file_dir + f'player_pos_{file_num}.npy')

input_data = gen_input(opp_regions, player_poss)

# global variables
data_num = 0
SCORE = 0
START = np.argwhere(input_data[data_num]==0)[0]
BOARD_ROWS = 7
BOARD_COLS = 10
WEIGHTS = input_data[data_num]
WIN_STATE = (3,-1)
DETERMINISTIC = True

# class State:
#     def __init__(self, state=START):
#         self.board = np.zeros([BOARD_ROWS, BOARD_COLS])
#         self.state = state
#         self.isEnd = False
#         self.score = 0
#         self.steps = 0
#         self.determine = DETERMINISTIC
#
#
#     def giveReward(self):
#         if self.state == WIN_STATE:
#             return 100
#         else:
#             return 0
#
#     def isEndFunc(self, steps):
#         if (self.state == WIN_STATE):
#             self.isEnd = True
#
#     def nxtPosition(self, action):
#         """
#         action: up, down, left, right
#         -------------
#         0 | 1 | 2| 3|
#         1 |
#         2 |
#         return next position
#         """
#         if self.determine:
#             if action == "up":
#                 nxtState = (self.state[0] - 1, self.state[1])
#             elif action == "down":
#                 nxtState = (self.state[0] + 1, self.state[1])
#             elif action == "left":
#                 nxtState = (self.state[0], self.state[1] - 1)
#             else:
#                 nxtState = (self.state[0], self.state[1] + 1)
#             # if next state legal
#             if (nxtState[0] >= 0) and (nxtState[0] <= 6):
#                 if (nxtState[1] >= 0) and (nxtState[1] <= 9):
#                     self.steps += 1
#                     return nxtState
#
#             return tuple(self.state)
#
#     def showBoard(self):
#         self.board[self.state] = 1
#         for i in range(0, BOARD_ROWS):
#             print('-----------------')
#             out = '| '
#             for j in range(0, BOARD_COLS):
#                 if self.board[i, j] == 1:
#                     token = '*'
#                 if self.board[i, j] == 0:
#                     token = '0'
#                 out += token + ' | '
#             print(out)
#         print('-----------------')
#
#
# # Agent of player
#
# class Agent:
#
#     def __init__(self):
#         self.states = []
#         self.actions = ["up", "down", "left", "right"]
#         self.State = State()
#         self.lr = 0.2
#         self.exp_rate = 0.3
#         self.steps = 0
#         self.weights = WEIGHTS
#
#         # initial state reward
#         self.state_values = {}
#         for i in range(BOARD_ROWS):
#             for j in range(BOARD_COLS):
#                 self.state_values[(i, j)] = self.weights[i,j]  # set initial value to 0
#
#     def chooseAction(self):
#         # choose action with most expected value
#         mx_nxt_reward = 0
#         action = ""
#
#         if np.random.uniform(0, 1) <= self.exp_rate:
#             action = np.random.choice(self.actions)
#         else:
#             # greedy action
#             for a in self.actions:
#                 # if the action is deterministic
#                 nxt_reward = self.state_values[self.State.nxtPosition(a)]
#                 if nxt_reward >= mx_nxt_reward:
#                     action = a
#                     mx_nxt_reward = nxt_reward
#         return action
#
#     def takeAction(self, action):
#         position = self.State.nxtPosition(action)
#         return State(state=position)
#
#     def reset(self):
#         self.states = []
#         self.State = State()
#
#     def play(self, rounds=10):
#         i = 0
#         while i < rounds:
#             # to the end of game back propagate reward
#             if self.State.isEnd:
#                 # back propagate
#                 reward = self.State.giveReward()
#                 # explicitly assign end state to reward values
#                 self.state_values[self.State.state] = reward  # this is optional
#                 print("Game End Reward", reward)
#                 for s in reversed(self.states):
#                     reward = self.state_values[s] + self.lr * (reward - self.state_values[s])
#                     self.state_values[s] = round(reward, 3)
#                 self.reset()
#                 i += 1
#             else:
#                 action = self.chooseAction()
#                 # append trace
#                 self.states.append(self.State.nxtPosition(action))
#                 print("current position {} action {}".format(self.State.state, action))
#                 # by taking the action, it reaches the next state
#                 self.State = self.takeAction(action)
#                 self.steps += 1
#
#                 # mark is end
#                 self.State.isEndFunc(self.steps)
#                 print("nxt state", self.State.state)
#                 print("---------------------")
#
#     def showValues(self):
#         for i in range(0, BOARD_ROWS):
#             print('----------------------------------')
#             out = '| '
#             for j in range(0, BOARD_COLS):
#                 out += str(self.state_values[(i, j)]).ljust(6) + ' | '
#             print(out)
#         print('----------------------------------')
#
# if __name__ == "__main__":
#     ag = Agent()
#     ag.play(10)
#     print(ag.showValues())

print('done')