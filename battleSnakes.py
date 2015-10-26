import pygame
import time
import random

pygame.init() 

white = (255, 255, 255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)

display_width = 800
display_height = 600

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Battle Snakes')

pygame.display.update()

FPS = 10

clock = pygame.time.Clock()

block_size = 10

font = pygame.font.SysFont(None, 25)

winner = 0

snakeHead1 = pygame.image.load('snakeHead1.png')
apple = pygame.image.load('apple.png')

direction1 = "left"
direction2 = "right"

def score(score1, score2):
	text1 = font.render("Score: "+str(score1), True, green)
	text2 = font.render("Score: "+str(score2), True, blue)
	gameDisplay.blit(text1, [0,0])
	gameDisplay.blit(text2, [720,0])

#functions for printing snakes
def snake1(snakelist1, block_size):
	'''
	if direction1 == "right":
		head1 = pygame.transform.rotate(snakeHead1, 270)
	if direction1 == "left":
                head1 = pygame.transform.rotate(snakeHead1, 90)
	if direction1 == "up":
                head1 = snakeHead1
	if direction1 == "down":
                head1 = pygame.transform.rotate(snakeHead1, 180)
	'''
	#gameDisplay.blit(head1, (snakelist1[-1][0], snakelist1[-1][1]))
	#for XnY in snakelist1[:-1]:
	for XnY in snakelist1:
		pygame.draw.rect(gameDisplay, green, [XnY[0], XnY[1], block_size, block_size])	

def snake2(snakelist2, block_size):
	for XnY in snakelist2:
                pygame.draw.rect(gameDisplay, blue, [XnY[0], XnY[1], block_size, block_size])

def text_objects(text, color):
	textSurface = font.render(text,True, color)
	return textSurface, textSurface.get_rect()

#function for printing message when game over
def message_to_screen(msg, color, y = 0):
	textSurf, textRect = text_objects(msg, color)
	textRect.center = (display_width/2), (display_height/2)+y
	gameDisplay.blit(textSurf, textRect)
	#screen_text = font.render(msg, True, color)
	#gameDisplay.blit(screen_text, [display_width/2, display_height/2])

def game_intro():
	intro = True
	while intro:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_p:
					intro = False

		gameDisplay.fill(white)
		message_to_screen("Welcome to battle snakes !", green, -100)
		message_to_screen("Press A to choose green snake and press B to choose blue snake !", green)
		message_to_screen("A = up", green, 50)
		message_to_screen("B = left", green, 100)
		message_to_screen("C = down", green, 150)
		message_to_screen("D = right", green, 200)
		
		message_to_screen("press P to play", red, 250)
	
		pygame.display.update()
		clock.tick(5)

#main game loop
def gameLoop():
	global winner
	global direction1
	global direction2
	
	direction1 = "left"
	direction2 = "right"

	#list of all coordinates for the snakes
	snakelist1 = [] 
	snakelist2 = []
	snakelength1 = 1
	snakelength2 = 1	

	#starting coordinates
	lead_x1 = display_width/2 - block_size 
	lead_y1 = display_height/2
	
	#change in starting coordinates
	lead_x_change1 = -10 
	lead_y_change1 = 0

	lead_x2 = display_width/2 + block_size
        lead_y2 = display_height/2
        lead_x_change2 = 10
        lead_y_change2 = 0	

	gameExit = False
	gameOver = False

	#random coordinates of the apple
	randAppleX = round(random.randrange(0, display_width - block_size)/10.0)*10.0
	randAppleY = round(random.randrange(0, display_height - block_size)/10.0)*10.0
	while not gameExit:
		global winner
		while gameOver == True:
			gameDisplay.fill(white)
			#print winner
			if winner == 1:
				message_to_screen("Green snake won, press Q to quit and P to play again", red)
				pygame.display.update()
			if winner == 2:
				message_to_screen("Blue snake won, press Q to quit and P to play again", red)
				pygame.display.update()
			if winner == 0:
				message_to_screen("TIED ! , press Q to quit and P to play again", red)
                       	        pygame.display.update()
			#winner = 0
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
                                	gameExit = True
                                	gameOver = False
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_q:
						gameExit = True
						gameOver = False
					if event.key == pygame.K_p:
						gameLoop()
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				gameExit = True
				gameOver = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					if direction1 != "right":
						direction1 = "left"
						lead_x_change1 = -block_size
						lead_y_change1 = 0
				if event.key == pygame.K_RIGHT:
					if direction1 != "left":
						direction1 = "right"
						lead_x_change1 = block_size
						lead_y_change1 = 0
				if event.key == pygame.K_UP:
					if direction1 != "down":
						direction1 = "up"
	                                	lead_y_change1 = -block_size
						lead_x_change1 = 0
	                        if event.key == pygame.K_DOWN:
					if direction1 != "up":
						direction1 = "down"
	                                	lead_y_change1 = block_size
						lead_x_change1 = 0
		
				if event.key == pygame.K_a:
					if direction2 != "right":
						direction2 = "left"
                                        	lead_x_change2 = -block_size
                                        	lead_y_change2 = 0
                                if event.key == pygame.K_d:
					if direction2 != "left":
						direction2 = "right"
                                        	lead_x_change2 = block_size
                                        	lead_y_change2 = 0
                                if event.key == pygame.K_w:
					if direction2 != "down":
						direction2 = "up"
                                        	lead_y_change2 = -block_size
                                        	lead_x_change2 = 0
                                if event.key == pygame.K_s:
					if direction2 != "up":
						direction2 = "down"
                                        	lead_y_change2 = block_size
                                        	lead_x_change2 = 0

		#when snake goes out of bounds
		if (lead_x1 >= display_width  or lead_x1 < 0 or lead_y1 >= display_height or lead_y1 < 0) and (lead_x2 >= display_width  or lead_x2 < 0 or lead_y2 >= display_height or lead_y2 < 0):
			gameOver = True
			winner = 0
			print 'tie'
		elif lead_x1 >= display_width  or lead_x1 < 0 or lead_y1 >= display_height or lead_y1 < 0:
			print 'out of bounds'
			gameOver = True
			winner = 2
			print winner
		elif lead_x2 >= display_width  or lead_x2 < 0 or lead_y2 >= display_height or lead_y2 < 0:
                        print 'out of bounds'
			gameOver = True
			winner = 1

		#update coordinates
		lead_x1 += lead_x_change1
		lead_y1 += lead_y_change1
		lead_x2 += lead_x_change2
                lead_y2 += lead_y_change2
		
		gameDisplay.fill(white)
		
		#draw random apple
		#pygame.draw.rect(gameDisplay, red, [randAppleX, randAppleY, block_size, block_size])
		gameDisplay.blit(apple, (randAppleX, randAppleY))

		#update lists
		snakehead1 = []
		snakehead1.append(lead_x1)
		snakehead1.append(lead_y1)
		snakelist1.append(snakehead1)

                snakehead2 = []
                snakehead2.append(lead_x2)
                snakehead2.append(lead_y2)
                snakelist2.append(snakehead2)
		
		#last element is head	
		
		#remove last element from list
		if len(snakelist1) > snakelength1:
			del snakelist1[0]
		if len(snakelist2) > snakelength2:
                        del snakelist2[0]
	
		#head-on collision
		if snakehead2 == snakehead1:
			print 'found head on'
			gameOver = True
			if len(snakelist1) > len(snakelist2):
				winner = 1
			elif len(snakelist2) > len(snakelist1):
				winner = 2
			else:
				winner = 0
		
		#checking for self collision	
		for each1 in snakelist1[:-1]:
			if each1 == snakehead1:
				gameOver = True
				winner = 2
			if each1 == snakehead2:
				gameOver = True
				winner = 1

		for each2 in snakelist2[:-1]:
			if each2 == snakehead2:
				gameOver = True
				winner = 1
			if each2 == snakehead1:
				gameOver = True
				winner = 2

		snake1(snakelist1, block_size)
		snake2(snakelist2, block_size)
		
		score(snakelength1 - 1, snakelength2 - 1)
	
		pygame.display.update()
		
		#if apple eaten, create new apple and update length
		if lead_x1 == randAppleX and lead_y1 == randAppleY:
			randAppleX = round(random.randrange(0, display_width - block_size)/10.0)*10.0
        		randAppleY = round(random.randrange(0, display_height - block_size)/10.0)*10.0
			snakelength1 += 1
		elif lead_x2 == randAppleX and lead_y2 == randAppleY:
                        randAppleX = round(random.randrange(0, display_width - block_size)/10.0)*10.0
                        randAppleY = round(random.randrange(0, display_height - block_size)/10.0)*10.0
			snakelength2 += 1

		clock.tick(FPS)
	
	pygame.quit()
	quit()

game_intro()
gameLoop()
