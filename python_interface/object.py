# ==============================================================================
# define object classes
# ==============================================================================
class Shoot:

    def __init__(self, unum, shot_scores):
        self.unum = unum
        self.scores = shot_scores


class Dribble:

    def __init__(self, unum, coord, target_point):
        self.unum = unum
        self.coord = coord
        self.target_point = target_point


class Pass(Dribble):

    def __init__(self, unum, coord, target_unum, target_point, through_point, pass_scores):
        self.target_unum = target_unum
        self.through_point = through_point
        self.scores = pass_scores
        Dribble.__init__(self, unum, coord, target_point)


class Ball:

    def __init__(self, ball):
        self.pos = ball[:2]
        self.vel = ball[2:]


class Player:

    def __init__(self, unum, players, holder, ball_dist):

        self.unum = unum
        self.pos = players[2:4]
        self.vel = players[4:6]
        self.kick_count = players[6]
        self.stam = players[7]
        self.stam_cap = players[8]

        self.ball_dist = ball_dist

        if holder == unum:
            self.holder = True
        else:
            self.holder = False
