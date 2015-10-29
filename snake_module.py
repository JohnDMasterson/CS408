import random
import math

class Snake:
        def __init__(self, board, snake_id, snake_color, snake_name, start_pos):
                self.snake_id = snake_id
                self.length = 1
		self.snake_name = snake_name
                self.snake_color = snake_color
                self.board = board
                self.head = start_pos
                self.snake_list = []
		self.direction = '0'
		self.direction_block = [0, 0]
                self.snake_list.append(self.head)
		board.make_block_occupied(start_pos[0], start_pos[1])

	def change_direction(self, new_direction):
		if new_direction == self.direction:
			return
		elif new_direction == self.opposite_direction(self.direction):
			return
		elif new_direction == 'u':
			self.direction_block = [0, -1]
			self.direction = new_direction
		elif new_direction == 'd':
			self.direction_block = [0, 1]
			self.direction = new_direction
		elif new_direction == 'l':
			self.direction_block = [-1, 0]
			self.direction = new_direction
		elif new_direction == 'r':
			self.direction_block = [1, 0]
			self.direction = new_direction
		else:
			#TODO Invalid input, throw an exception?
			self.direction = self.direction

	def self_collided(self):
		for each in self.snake_list[:-1]:
			if each == self.head:
				print "Self collision"
				return True
		return False

	def collided(self, other_snake):
		if self.self_collided():
			return True
		for each in other_snake.snake_list[:-1]:
			if each == self.head:
				print "Collision"
				return True
                return False

	def opposite_direction(self, new_direction):
		if new_direction == 'u':
			return 'd'
                elif new_direction == 'd':
			return 'u'
                elif new_direction == 'l':
			return 'r'
                elif new_direction == 'r':
			return 'l'
		else:
			return '0'

        def increase_length(self):
                self.length += 1

        def decrease_length(self):
                if(self.length >= 2):
                        self.length -= 1
                elif(self.length == 1):
                        #TODO this is an edge case
                        self.length = self.length
                else:
                        #TODO what should be done?
                        self.length = self.length

	def out_of_bounds(self):
		if self.head[0] >= self.board.num_hor_blocks or self.head[0] < 0:
			return True
		elif self.head[1] >= self.board.num_ver_blocks or self.head[1] < 0:
			return True
		else:
			return False

        def move(self):
                #this is only updating the internal representation of the snake
                x = self.head[0] + self.direction_block[0]
                y = self.head[1] + self.direction_block[1]
                self.head = [x, y]
		self.snake_list.append(self.head)
		self.board.make_block_occupied(x, y)

		while len(self.snake_list) > self.length:
			trash = self.snake_list[0]
			self.board.make_block_empty(trash[0], trash[1])
			del self.snake_list[0]

class Board:
        #empty_blockks is represented as an integer that inceases from 1 in the
        #top left corner
        #to height*width in the bottom right corner
        #it increase left to right and up to down

        #width, height, block_size are in pixels
        def __init__(self, width, height, block_size):
                #Width and height are floored to contain integer number of blocks
                self.num_hor_blocks = int(math.floor(width/block_size))
		self.num_ver_blocks =  int(math.floor(height/block_size))
                self.width = self.num_hor_blocks*block_size
                self.height = self.num_ver_blocks*block_size
		self.margin = int(0.5*(height - self.height))
                self.block_size = int(block_size)
                self.empty_blocks = range(1, self.num_hor_blocks * self.num_ver_blocks+1)

	def int_to_point(self, num):
		return [(num - 1)%self.num_hor_blocks, int(math.floor((num - 1) /self.num_hor_blocks))]

        def random_empty_block(self):
                return self.int_to_point(random.choice(self.empty_blocks))

        def point_to_int(self, x, y):
                return (x+1)+(y*self.num_hor_blocks)

        def make_block_empty(self, x, y):
                pos = self.point_to_int(x, y)
                if not pos in self.empty_blocks:
                        self.empty_blocks.append(pos)

        def make_block_occupied(self, x, y):
                pos = self.point_to_int(x, y)
                if pos in self.empty_blocks:
                        self.empty_blocks.remove(pos)

class GameInput:
	def __init__(self, key, count):
		self.key = key
		self.count = count
