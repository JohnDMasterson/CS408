from iclicker import *
import time
import threading
from collections import defaultdict, Counter


current_milli_time = lambda: int(round(time.time() * 1000))

class iclickerII:
	def __init__(self):
		self.poll = iClickerPoll()
		self.poll.start_poll()

	def create_groups(self, identifiers):
		#reset the previously recevied inputs
		self.restart_poll()
		self.identifiers = identifiers

	def stop_grouping(self):
		char_identifiers = self.identifiers
		identifiers = []
		for i in char_identifiers:
			identifiers.append(str(ord(i.upper())))
                old_iClickerResponses = self.poll.iClickerResponses
		self.groups = defaultdict()
		#parse the responses
		for clickerId in old_iClickerResponses:
			responses = old_iClickerResponses[clickerId]
			#check response and assign group
			group = 1
			for ident in identifiers:
				if ident == str(responses[-1].response):
					self.groups[clickerId] = group
				group += 1
		print self.groups

	def start_poll(self):
		if self.poll.isPolling is False:
			self.poll.isPolling = True
			self.poll.start_poll()
		self.poll.iClickerResponses = defaultdict(list)

	def stop_poll(self):
		self.poll.end_poll

	def current_group_responses(self):
		o = len(self.identifiers) - 1
		return_val = [5*[0]]
		while o > 0:
			return_val.append(5*[0])
			o -= 1
		for clickerId in self.poll.iClickerResponses:
			responses = self.poll.iClickerResponses[clickerId]
			if clickerId in self.groups:
				return_val[(self.groups[clickerId] - 1)][(responses[-1].response - ord('A'))] += 1
		return return_val

	def current_responses(self):
		return_val = 5*[0]
                for clickerId in self.poll.iClickerResponses:
                        responses = self.poll.iClickerResponses[clickerId]
                        return_val[responses[-1].response - ord('A')] += 1
                return return_val
		
	def get_group_count(self, group):
		count = 0
                #parse the responses
                for clickerId in self.poll.iClickerResponses:
                        if self.groups[clickerId] == group:
				count += 1
		return count

	def get_num_users(self):
                return len(self.poll.iClickerResponses)

	def set_frequency(self, freq):
		valid_chars = ['A', 'B', 'C', 'D', 'E']

		for c in valid_chars:
			if not freq[0] == c or freq[1] == c:
				#TODO throw exception
				return
		
		self.stop_poll()
		#change frequency
		self.poll.iClickerBase.set_frequency(freq[0], freq[1])
		#start poll
		self.start_poll()

	def get_frequency(self):
		return "".join(self.poll.iClickerBase.frequency)

	def get_individual_response(self, clicker_id):
		return chr(self.poll.iClickerResponses[clicker_id][-1].response)

	def get_individual_response_count(self, clicker_id):
		return len(self.poll.iClickerResponses[clicker_id])

	def get_most_frequent_user(self):
		max_resp = 0
		max_id = None
                for clickerId in self.poll.iClickerResponses:
                        responses = self.poll.iClickerResponses[clickerId]
			if len(responses) > max_id:
				max_id = clickerId
				max_resp = len(responses)
		return max_id

	def restart_poll(self):
		self.poll.iClickerResponses = defaultdict(list)

#poll = iclickerII()
#print "Starting"
#poll.create_groups(['A','B','C','D','E'])
#time.sleep(10)
#poll.stop_grouping()
#poll.set_frequency("AD")
#print poll.groups
