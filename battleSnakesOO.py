try:
	import pygame
except ImportError:
	print "Hissss! An error occured while importing pygame. See http://pygame.org/wiki/GettingStarted for installation instructions"
	quit()
import time
from snake_module import *

current_milli_time = lambda: int(round(time.time() * 1000))
pygame.init()

white = (255, 255, 255)
black = (0,0,0)
grey = (125, 125, 125)
red = (255,0,0)
green = (0,150,0)
blue = (0,0,255)
beige = (240, 240, 190)

display_width = 800
display_height = 600

panel_width = 300
gameDisplay = pygame.display.set_mode((display_width + panel_width, display_height))
pygame.display.set_caption('Battle Snakes')
pygame.display.update()
FPS = 1
clock = pygame.time.Clock()
block_size = 20
font = pygame.font.SysFont(None, 30)
second_font = pygame.font.SysFont(None, 22)
score_font = pygame.font.SysFont(None, 25)

text_board = pygame.image.load('text_board.png')

board = Board(display_width, display_height, block_size)
start_pos = board.random_empty_block()
snakeA = Snake(board, 1, green, "Green", start_pos)
start_pos = board.random_empty_block()
snakeB = Snake(board, 2, blue, "Blue", start_pos)
winner = None
gameExit = False
gameOver = False
game_over_shown = False

image1 = pygame.transform.scale(pygame.image.load('apple.png'), (block_size, block_size))
image2 = pygame.transform.scale(pygame.image.load('apple2.png'), (block_size, block_size))

appleA = Apple(0, 0, image1, 1)
appleB = Apple(0, 0, image2, -1)

appleA.pos = board.random_empty_block()
appleB.pos = board.random_empty_block()
apples = [appleA, appleB]

#function for printing message when game over
def message_to_screen(msg_title, color, msg_text=None):
	screen_text = font.render(msg_title, True, color)
	text_board_rect = text_board.get_rect(center=(display_width/2, display_height/2))
	if not msg_text is None:
		screen_text2 = second_font.render(msg_text, True, color)
		text_rect = screen_text.get_rect(center=(display_width/2, display_height/2 - 15))
		text2_rect = screen_text2.get_rect(center=(display_width/2, display_height/2 + 15))
	else:
		text_rect = screen_text.get_rect(center=(display_width/2, display_height/2))
	gameDisplay.blit(text_board, text_board_rect)
	gameDisplay.blit(screen_text, text_rect)
	if not msg_text is None:
		gameDisplay.blit(screen_text2, text2_rect)


def print_snake(snake):
	board = snake.board
	for XnY in snake.snake_list:
		pygame.draw.rect(gameDisplay, snake.snake_color, [board.margin + board.block_size*XnY[0], board.margin + board.block_size*XnY[1], board.block_size, board.block_size])
	#draw eyes
	XnY = snake.snake_list[-1]
	eyes = pygame.surface.Surface((board.block_size, board.block_size))
	eyes.fill(snake.snake_color)
	pygame.draw.circle(eyes, black, (board.block_size/4, board.block_size/4), board.block_size/8)
	pygame.draw.circle(eyes, black, (3*board.block_size/4, board.block_size/4), board.block_size/8)
	if snake.direction == 'd':
		eyes = pygame.transform.rotate(eyes, 180)
	elif snake.direction == 'l':
		eyes = pygame.transform.rotate(eyes, 90)
	elif snake.direction == 'r':
		eyes = pygame.transform.rotate(eyes, -90)
	board = snake.board
	gameDisplay.blit(eyes, (board.margin+board.block_size*XnY[0], board.margin+board.block_size*XnY[1]))


def game_over(winner_snake, game_input=None):
	global game_over_shown 
	if not game_over_shown:
		if winner_snake is None:
			message_to_screen("Game Over!", black, "It's a tie! Press 'A' to play again or 'B' to quit")
		else:
			message_to_screen("Game Over!", black, winner_snake.snake_name+" snake wins. Press 'A' to play again or 'B' to quit")
		game_over_shown = True


def edge_case_winner(snakeA, snakeB):
	#no winner or winner is longer snake
	if snakeA.length > snakeB.length:
		return snakeA
	elif snakeB.length > snakeA.length:
		return snakeB
	else:
		#no winner
		return None


def score(score1, score2):
	text1 = font.render("Score: "+str(score1), True, green)
	text2 = font.render("Score: "+str(score2), True, blue)
	gameDisplay.blit(text1, [0,0])
	gameDisplay.blit(text2, [720,0])


def draw_game():
	pygame.draw.rect(gameDisplay, grey, [board.margin - 1, board.margin - 1, board.width+2, board.height+2], 1)
	pygame.draw.rect(gameDisplay, beige, [board.margin, board.margin, board.width, board.height])
	score(snakeA.length - 1, snakeB.length - 1)
	print_snake(snakeA)
	print_snake(snakeB)
	gameDisplay.blit(appleA.image, (board.block_size*appleA.pos[0]+board.margin, board.block_size*appleA.pos[1]+board.margin))
	gameDisplay.blit(appleB.image, (board.block_size*appleB.pos[0]+board.margin, board.block_size*appleB.pos[1]+board.margin))

#game_input is a two element list.
#the first is the input from the first team
#the second is the input from the second
#note that the elements of the list are GameInput objects
def gameloop(game_input):
	global gameOver, gameExit, winner, appleA, appleB

	if not gameExit:
		if gameOver:
			#draw_game()
			#show game over text
			game_over(winner, game_input)
			#print "game over"
		else:
			if not game_input is None:
				snakeA.change_direction(game_input[0].key)
				snakeB.change_direction(game_input[1].key)
			#update snake location
			snakeA.move()
			snakeB.move()

			#check if snakes collided
			if(snakeA.head == snakeB.head):
				winner = edge_case_winner(snakeA, snakeB)
				print "Collision"
				gameOver = True
				game_over(winner)
				return
			#check if snakes are out of bounds
			elif snakeA.out_of_bounds() and snakeB.out_of_bounds():
				winner = edge_case_winner(snakeA, snakeB)
				print "Out of Bounds"
				gameOver = True
				game_over(winner)
				return
			elif snakeA.out_of_bounds():
				winner = snakeB
				print "Out of BoundA"
				gameOver = True
				game_over(winner)
				return
			elif snakeB.out_of_bounds():
				winner = snakeA
				print "Out of Bounds B"
				gameOver = True
				game_over(winner)
				return
			#check for collision (self collision is also collision)
			if snakeA.collided(snakeB) or snakeB.collided(snakeA):
				if snakeA.collided(snakeB) and snakeB.collided(snakeA):
					winner = edge_case_winner(snakeA, snakeB)
				elif snakeA.collided(snakeB):
					winner = snakeB
				else:
					winner = snakeA
				print "Collided"	
				gameOver = True
				game_over(winner)
				return
			#check if apples got eaten
			for apple in apples:
				if snakeA.head == apple.pos:
					if apple.effect is 1:
						snakeA.increase_length()
					elif apple.effect is -1:
						snakeA.decrease_length()
						if snakeA.length <= 0:
							gameOver = True
							winner = snakeB
							game_over(winner)
							return
					board.make_block_empty(apple.pos[0], apple.pos[1])
					#create new apple
					apple.pos = board.random_empty_block()
				elif snakeB.head == apple.pos:
					if apple.effect is 1:
                                                snakeB.increase_length()
                                        elif apple.effect is -1:
                                                snakeB.decrease_length()
						if snakeB.length <= 0:
                                                        gameOver = True
                                                        winner = snakeA
                                                        game_over(winner)
                                                        return

					board.make_block_empty(apple.pos[0], apple.pos[1])
					apple.pos = board.random_empty_block()
			#draw all the stuff
			if not gameOver:
				draw_game()
	else:
		pygame.quit()
		quit()

def next_frame_time():
	global last_frame_time

	diff = 1000.0/FPS
	if current_milli_time() - last_frame_time >= diff:
		last_frame_time = current_milli_time()
		return True
	else:
		return False

def clamp(min_num, max_num, num):
	if num < min_num:
		return min_num
	elif num > max_num:
		return max_num
	else:
		return num

def update_time_bar():
	ratio = clamp(0, 1, FPS*(current_milli_time() - last_frame_time)/1000.0)
	color_change = int(255*ratio)
	color = (0+color_change, 255-color_change, 0)
	pygame.draw.rect(gameDisplay, color, [2*board.margin + 15 + board.width, board.margin + board.height/2 - 15, panel_width - 30, 20], 2)
	pygame.draw.rect(gameDisplay, grey, [2*board.margin + 15 + board.width + 4, board.margin + board.height/2 - 15 + 4, (1 - ratio) * (panel_width - 38), 13])

def clear_panel():
	pygame.draw.rect(gameDisplay, white, [display_width, 0, panel_width, display_height])

def clear_raw_inputs():
	global raw_inputs, inputs
	inputs = [GameInput('u', 0), GameInput('d', 0)]
	raw_inputs = [[GameInput('u', 0), GameInput('r', 0), GameInput('d', 0), GameInput('l', 0)], [GameInput('u', 0), GameInput('r', 0), GameInput('d', 0), GameInput('l', 0)]]

def update_inputs():
	global inputs, raw_inputs
	index = 0
	for keys in raw_inputs:
		key = random.choice(['u', 'd', 'l', 'r'])
		for k in keys:
			if key == k.key:
				k.count += 1
				if k.count > inputs[index].count:
					inputs[index] = k
				break
		index += 1

def print_inputs():
        global inputs, raw_inputs
	print "========="
        for keys in raw_inputs:
                for k in keys:
			print k.count
		print ""
	print ""

inputs = None
raw_inputs = None
clear_raw_inputs()
gameDisplay.fill(white)
last_frame_time = current_milli_time()
draw_game()
pygame.display.update()

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			quit()
	update_inputs()
	clear_panel()
	update_time_bar()
	if next_frame_time():
		gameloop(inputs)
		#print_inputs()
		clear_raw_inputs()
	pygame.display.update()
