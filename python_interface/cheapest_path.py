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
file_num = 1

regions = np.load(file_dir + f'regions_{file_num}.npy')
team_regions = np.load(file_dir + f'team_regions_{file_num}.npy')
opp_regions = np.load(file_dir + f'opp_regions_{file_num}.npy')
player_poss = np.load(file_dir + f'player_pos_{file_num}.npy')

input_data = gen_input(opp_regions, player_poss)

# global variables
BOARD_ROWS = 7
BOARD_COLS = 10
data_num = -111
WIN_STATE = (3,9)


class board:

    def __init__(self, data_num):

        self.data_num = data_num
        self.actions = ['right', 'up', 'down', 'upright', 'downright']
        self.weights = input_data[data_num]
        self.start = tuple(np.argwhere(input_data[data_num] == 0)[0])
        self.end = WIN_STATE
        self.board = np.zeros([BOARD_ROWS, BOARD_COLS])
        self.state = np.array(self.start)
        self.last_action = ['']
        self.isEnd = False

    def moves(self, action):
        return_position = False
        next_state = self.state.copy()
        if action == 'right':
            next_state[1] += 1
        elif action == 'up':
            next_state[0] -= 1
            if self.last_action[-1] == 'down':
                return_position = True
        elif action == 'down':
            next_state[0] += 1
            if self.last_action[-1] == 'up':
                return_position = True
        elif action == 'upright':
            next_state[0] -= 1
            next_state[1] += 1
        elif action == 'downright':
            next_state[0] += 1
            next_state[1] += 1

        if 0 <= next_state[0] <= BOARD_ROWS-1 and 0 <= next_state[1] <= BOARD_COLS-1 and not return_position:
            next_weight = self.weights[tuple(next_state)]
            return next_weight, next_state
        return -1000, self.state

    def isEndFunc(self):
        if (self.state == np.array(WIN_STATE)).all():
            self.isEnd = True


    def play(self, round):

        all_scores = []
        all_moves = []
        i = 0
        while i < round:
            if self.isEnd:
                scores = np.sum(self.weights*self.board)
                all_moves.append(self.board.copy())
                all_scores.append(scores)
                # print(scores)
                i += 1
                self.__init__(self.data_num)

            else:

                next_move = []
                next_weight = []
                for action in self.actions:
                    weight, state = self.moves(action)
                    next_weight.append(weight)
                    next_move.append(state)
                next_weight = np.array(next_weight)

                if (next_weight > 0).any():
                    ind = int(np.argwhere(next_weight==next_weight.max())[0])
                else:
                    p = np.divide(np.ones(len(next_weight)), 0-next_weight, out=np.zeros_like(np.ones(len(next_weight))), where=(0-next_weight)!=0)
                    p = p/sum(p)
                    ind = int(np.random.choice(len(self.actions), 1, replace=False, p=p))
                self.state = next_move[ind]
                self.last_action.append(self.actions[ind])
                self.board[tuple(self.state)] += 1
                self.isEndFunc()
        all_scores = np.array(all_scores)
        index = int(np.argwhere(all_scores==all_scores.max())[0])

        # print(index)
        # print(all_moves[index])

        return all_scores[index], all_moves[index]

if __name__ == '__main__':

    scores = []
    moves = []

    for i in range(len(input_data)):

        score, move = board(i).play(1000)
        scores.append(score)
        moves.append(move)
        print(i)

    np.save('scores1.npy',np.dstack(scores))
    np.save('moves1.npy',np.dstack(moves))




#
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
#         elif self.steps > 15:
#             return -1
#
#     def isEndFunc(self, steps):
#         if (self.state == WIN_STATE) or steps > 15:
#             self.steps = steps
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
#
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
#         self.actions = ["up", "down", "right"]
#         self.opp_actions = ["down", "up", "left"]
#         self.last_action = ""
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
#             for j in range(len(self.actions)):
#                 a = self.actions[j]
#                 if self.opp_actions[j] != self.last_action:
#
#                     # if the action is deterministic
#                     nxt_reward = self.state_values[self.State.nxtPosition(a)]
#                     if nxt_reward >= mx_nxt_reward:
#                         action = a
#                         mx_nxt_reward = nxt_reward
#                     self.last_action = a
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
#     def play(self, rounds=None):
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
#     ag.play(rounds=10000)
#     print(WEIGHTS)
#     print(ag.showValues())

print('done')
