# from world_model import World_Model


class Agent:

	def __init__(self, World_Model):

		self.wm = World_Model
		print('ball_holder: '+str(self.wm.ball_holder))

		self.wm.move([0,5])
		self.wm.chain([9, 1, 50, 35, 9])