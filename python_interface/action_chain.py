from utils import caldist
import numpy as np


class Action_Chain:

    def __init__(self, scores, players, shoots, passes, dribbles):

        self.actions = []
        self.actions.extend(dribbles)
        self.actions.extend(passes)
        self.actions.extend(shoots)

        self.scores = scores
        self.players = players
        try:
            self.weights = np.load('weights.npy')
        except:
            self.weights = np.ones([5, 1])

        self.std_scores()

    def std_scores(self):

        for a in self.actions:
            # 1 is dribbles
            if a.cat < 3:
                a.score -= a.goal_dist/100


    def act_conv(self, action):
        '''
        convert action into a list for parser to read
        '''
        return [action.unum, action.cat, action.target_point[0], action.target_point[1], action.target_unum]

    def act_gen(self):
        best_score = -10
        best_it = -10

        it = 0
        for a in self.actions:
            if a.score > best_score:
                best_score = a.score
                best_it = it
            it +=1
        return self.act_conv(self.actions[best_it])
