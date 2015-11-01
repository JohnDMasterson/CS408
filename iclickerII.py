from iclicker import *

class iclickerII:
	def __init__(self):
		self.poll = iClickerPoll()

	def createGroups(self, num_of_gropus, identifiers, time, callback=None):
		self.poll.start_Poll()
