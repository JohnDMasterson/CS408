try:
	import pygame
except ImportError:
	print "Dang! An error occured while importing pygame. See http://pygame.org/wiki/GettingStarted for installation instructions"
	quit()
import time
import snake_module

pygame.init()

white = (255, 255, 255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
beige = (240, 240, 173)

display_width = 800
display_height = 618

panel_width = 300
gameDisplay = pygame.display.set_mode((display_width + panel_width, display_height))
pygame.display.set_caption('Battle Snakes')
pygame.display.update()
FPS = 1
clock = pygame.time.Clock()
block_size = 20
font = pygame.font.SysFont(None, 25)
apple = pygame.image.load('apple.png')
apple = pygame.transform.scale(apple, (block_size, block_size))

board = snake_module.Board(display_width, display_height, block_size)
start_pos = board.random_empty_block()
snakeA = snake_module.Snake(board, 1, green, "Green", start_pos)
start_pos = board.random_empty_block()
snakeB = snake_module.Snake(board, 2, red, "Red", start_pos)
winner = None
gameExit = False
gameOver = False
apple_pos = board.random_empty_block()

#function for printing message when game over
def message_to_screen(msg, color):
	s = pygame.Surface((1000,750))  # the size of your rect
	s.set_alpha(128)                # alpha level
	s.fill((255,255,255))           # this fills the entire surface
	windowSurface.blit(s, (0,0))    # (0,0) are the top-left coordinates
	screen_text = font.render(msg, True, color)
	gameDisplay.blit(screen_text, [display_width/2, display_height/2])

def print_snake(snake):
	board = snake.board
        for XnY in snake.snake_list:
                pygame.draw.rect(gameDisplay, snake.snake_color, [board.margin + board.block_size*XnY[0], board.margin + board.block_size*XnY[1], board.block_size, board.block_size])

def game_over(winner_snake, game_input=None):
	p = 'p'

def edge_case_winner(snakeA, snakeB):
	#no winner or winner is longer snake
	if snakeA.length > snakeB.length:
		return snakeA
	elif snakeB.length > snakeA.length:
		return snakeB
	else:
		#no winner
		return None

def draw_game():
	pygame.draw.rect(gameDisplay, beige, [board.margin, board.margin, board.width, board.height])
	print_snake(snakeA)
	print_snake(snakeB)
	gameDisplay.blit(apple, (board.block_size*apple_pos[0]+board.margin, board.block_size*apple_pos[1]+board.margin))

#game_input is a two element list.
#the first is the input from the first team
#the second is the input from the second
#note that the elements of the list are GameInput objects
def gameloop(game_input):
	global gameOver, gameExit, winner, apple_pos

	if not gameExit:
		if gameOver:
			#show game over text
			game_over(winner, game_input)
			#print "game over"
		else:
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
			#check if snakes are out of bounds
			elif snakeA.out_of_bounds() and snakeB.out_of_bounds():
				winner = edge_case_winner(snakeA, snakeB)
				print "Out of Bounds"
				gameOver = True
				game_over(winner)
			elif snakeA.out_of_bounds():
				winner = snakeB
				print "Out of BoundA"
				gameOver = True
				game_over(winner)
			elif snakeB.out_of_bounds():
				winner = snakeB
				print "Out of Bounds B"
				gameOver = True
				game_over(winner)
			#check for self_collision
			elif snakeA.self_collided() or snakeB.self_collided():
				if snakeA.self_collided() and snakeB.self_collided():
					winner = edge_case_winner(snakeA, snakeB)
				elif snakeA.self_collided():
					winner = snakeB
				else:
					winner = snakeA
				print "Self Collided"	
				gameOver = True
				game_over(winner)
			#check if apple got eaten
			elif snakeA.head == apple_pos:
				snakeA.increase_length()
				board.make_block_empty(apple_pos[0], apple_pos[1])
				#create new apple
				apple_pos = board.random_empty_block()
			elif snakeB.head == apple_pos:
				snakeB.increase_length()
				board.make_block_empty(apple_pos[0], apple_pos[1])
				apple_pos = board.random_empty_block()
			#draw all the stuff
			if not gameOver:
				draw_game()
	else:
		pygame.quit()
		quit()

inputs = [snake_module.GameInput('u', 5), snake_module.GameInput('d', 5)]
test = True
gameDisplay.fill(white)
draw_game()

while test:
	gameDisplay.fill(white)
	gameloop(inputs)
	pygame.display.update()
	clock.tick(FPS)
