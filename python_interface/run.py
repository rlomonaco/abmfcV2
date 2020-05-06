from world_model import World_Model
from agent import Agent
# ==============================================================================
# define variables
# ==============================================================================

HOST = "localhost"
PORT = 8889
MOVE_PORT = 7777
CHAIN_PORT = 6666

# ==============================================================================
# define class
# ==============================================================================
class run:

	def __init__(self):

		self.wm = World_Model(HOST, PORT, MOVE_PORT, CHAIN_PORT)
	def main(self):

		while True:

			self.wm.update()
			# self.wm.move([[0,1],[0,2],[0,3]])
			# self.wm.chain([0,1,2,3,4,5])





if __name__ == "__main__":

	run().main()