try:
	import pygame
except ImportError:
	print "Hissss! An error occured while importing pygame. See http://pygame.org/wiki/GettingStarted for installation instructions"
	quit()
import time
try:
	import iclickerII
except ImportError:
	print "Hissss! An error occured, verify that iclickerII.py exists and is in the same directory"
	quit()
try:
	from snake_module import *
except ImportError:
	print "Hissss! An error occured, verify that snake_module.py exists and is in the same directory"
	quit()

try:
	poll = iclickerII.iclickerII()
except AttributeError:
	print "iClicker base not detected, please verify USB connection"
	quit()

#poll.set_frequency("AB")

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
graph_font = pygame.font.SysFont(None, 20)

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

def make_input_graph(inputs, color):
	keys = ['A', 'B', 'C', 'D']
	keys2 = ["UP", "LEFT", "RIGHT", "DOWN"]
	graph_size = panel_width - 32
	xPos = 0.20*graph_size
	yPos = 4*[0]
	maxWidth = 0.75 * graph_size
	height = graph_size/8
	off = 0.5*height

	for i in range(0,4):
		yPos[i] = off
		off += 2*height
	total = 0.0

	content = pygame.Surface((graph_size, graph_size))
        content.fill(white)
	pygame.draw.line(content, color, (xPos, graph_size/32), (xPos, 31*graph_size/32), 2)

	for inp in inputs:
		total += inp.count
	i = 0
	for inp in inputs:
		if total == 0:
			width = 0
		else:
			width = maxWidth*inp.count/total
		label1 = graph_font.render(keys[i], True, color)
                label2 = graph_font.render(keys2[i], True, color)
		pygame.draw.rect(content, color, [xPos, yPos[i], width, height])
		content.blit(label1, [5, yPos[i]])
		content.blit(label2, [5, yPos[i]+20])
		label3 = graph_font.render(str(inp.count), True, black)
		content.blit(label3, [xPos+5, yPos[i] + height/2 - 5])
		i += 1
	border = pygame.Surface((graph_size+2, graph_size+2))
	border.fill(grey)
	border.blit(content, [1,1])
	return border

def update_input_graphs():
	graph1 = make_input_graph(raw_inputs[0], snakeA.snake_color)
	graph2 = make_input_graph(raw_inputs[1], snakeB.snake_color)
	gameDisplay.blit(graph1, [display_width+15, 10])
	gameDisplay.blit(graph2, [display_width+15, display_height/2 + 10 + 12])

def text_objects(text, color):
        textSurface = font.render(text,True, color)
        return textSurface, textSurface.get_rect()

def old_message_to_screen(msg, color, y = 0):
        textSurf, textRect = text_objects(msg, color)
        textRect.center = (display_width/2), (display_height/2)+y
        gameDisplay.blit(textSurf, textRect)
        #screen_text = font.render(msg, True, color)
        #gameDisplay.blit(screen_text, [display_width/2, display_height/2])

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
	global game_over_shown, gameOver 
	if not game_over_shown:
		if winner_snake is None:
			message_to_screen("Game Over!", black, "It's a tie! Press 'A' to play again or 'B' to quit")
		else:
			message_to_screen("Game Over!", black, winner_snake.snake_name+" snake wins. Press 'A' to play again or 'B' to quit")
		game_over_shown = True
	if not game_input is None:
		inp = game_input[1]
		if game_input[0].count > game_input[1].count:
			inp = game_input[0]
		if inp.key is 'u':#A
			snakeA.reset_snake(board.random_empty_block())
			snakeB.reset_snake(board.random_empty_block())
			game_over_shown = False
			gameOver = False
			draw_game()
		elif inp.key is 'l': #B
			quit()

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
			#check if snakes are out of bounds
			elif snakeA.out_of_bounds() and snakeB.out_of_bounds():
				winner = edge_case_winner(snakeA, snakeB)
				print "Out of Bounds"
				gameOver = True
			elif snakeA.out_of_bounds():
				winner = snakeB
				print "Out of BoundA"
				gameOver = True
			elif snakeB.out_of_bounds():
				winner = snakeA
				print "Out of Bounds B"
				gameOver = True
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
			#check if apples got eaten
			for apple in apples:
				if snakeA.head == apple.pos:
					if apple.effect is 1:
						snakeA.increase_length()
					elif apple.effect is -1:
						snakeB.decrease_length()
						if snakeB.length <= 0:
							gameOver = True
							winner = snakeA
					board.make_block_empty(apple.pos[0], apple.pos[1])
					#create new apple
					apple.pos = board.random_empty_block()
				elif snakeB.head == apple.pos:
					if apple.effect is 1:
                                                snakeB.increase_length()
                                        elif apple.effect is -1:
                                                snakeA.decrease_length()
						if snakeA.length <= 0:
                                                        gameOver = True
                                                        winner = snakeB

					board.make_block_empty(apple.pos[0], apple.pos[1])
					apple.pos = board.random_empty_block()
			draw_game()
                        #draw all the stuff
                        if gameOver:
                                game_over(winner)
	else:
		pygame.quit()
		quit()

def next_frame_time(duration):
	global last_frame_time

	diff = duration*1000.0#/FPS
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

def update_time_bar(duration):
	ratio = clamp(0, 1, (current_milli_time() - last_frame_time)/(1000.0*duration))
	color_change = int(255*ratio)
	color = (0+color_change, 255-color_change, 0)
	pygame.draw.rect(gameDisplay, color, [2*board.margin + 15 + board.width, board.margin + board.height/2 - 10, panel_width - 30, 20], 2)
	pygame.draw.rect(gameDisplay, grey, [2*board.margin + 15 + board.width + 4, board.margin + board.height/2 - 10 + 4, (1 - ratio) * (panel_width - 38), 13])

def clear_panel():
	pygame.draw.rect(gameDisplay, white, [display_width+5, 0, panel_width, display_height])

def clear_raw_inputs():
	global raw_inputs, inputs
	if inputs is None:
		inputs = [GameInput('u', 0), GameInput('u', 0)]
	for inp in inputs:
		inp.count = 0
	raw_inputs = [[GameInput('u', 0), GameInput('l', 0), GameInput('r', 0), GameInput('d', 0)], [GameInput('u', 0), GameInput('l', 0), GameInput('r', 0), GameInput('d', 0)]]

def update_inputs():
	global inputs, raw_inputs
	i = 0
	j = 0
	for group in poll.current_group_responses():
		j = 0
		for resp in group[:4]:
			raw_inputs[i][j].count = resp
			if raw_inputs[i][j].count > inputs[i].count:
				inputs[i] = raw_inputs[i][j]
			j += 1
		i += 1

def game_intro():
	gameDisplay.fill(white)
        old_message_to_screen("Welcome to battle snakes !", green, -100)
        old_message_to_screen("Press A to choose green snake and press B to choose blue snake !", green)
        old_message_to_screen("A = up", green, 50)
        old_message_to_screen("B = left", green, 100)
        old_message_to_screen("C = right", green, 150)
        old_message_to_screen("D = down", green, 200)
        #old_message_to_screen("press P to play", red, 250)

def print_inputs():
        global inputs, raw_inputs
	print "========="
        for keys in raw_inputs:
                for k in keys:
			print k.count
		print ""
	print ""
duration = 10#1.0/FPS
inputs = None
raw_inputs = None
clear_raw_inputs()
gameDisplay.fill(white)
last_frame_time = current_milli_time()
draw_game()
intro = True
pygame.display.update()

poll.create_groups(['A', 'B'])

while intro:
	time.sleep(0.01)
	game_intro()
	for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        quit()
	clear_panel()
        update_time_bar(duration)

	if next_frame_time(duration):
		intro = False
	pygame.display.update()

poll.stop_grouping()
duration = 1.0/FPS
gameDisplay.fill(white)
last_frame_time = current_milli_time()
draw_game()

while True:
	time.sleep(0.01)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			quit()
	update_inputs()
	clear_panel()
	update_time_bar(duration)
	update_input_graphs()
	if next_frame_time(duration):
		gameloop(inputs)
		poll.restart_poll()
		#print_inputs()
		clear_raw_inputs()
		if gameOver:
			duration = 5
		else:
			duration = 1.0/FPS
	pygame.display.update()
