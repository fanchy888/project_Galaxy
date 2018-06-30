# -*- coding: utf-8 -*-
from vector import Vector2
import pygame
from pygame.locals import *
from sys import exit
import random
from entities import *
		
		
screen=pygame.display.set_mode((1080,720),0,32)
pygame.display.set_caption('biu~~')	
clock=pygame.time.Clock()	
pygame.init()
	
ship=pygame.image.load('armstrong.png').convert_alpha()	
gears=[-1,0,2,4]	
world=Space()
s1=Spacecraft(ship,world)
e1=Engine(s1,500,'test',gears,['gas,nuclear,solar'])	
s1.add_engine(e1)
f1=Energy(['gas',1,20,1])	
s1.fill_tank(f1)
world.ship=s1
while True:
	screen.fill((200,255,255))
	buttons=pygame.mouse.get_pressed()
	for event in pygame.event.get():	
		if event.type==QUIT:
			exit()
		if event.type==pygame.MOUSEBUTTONUP and buttons[0]:
			if s1.engine.gear_id<3:
				s1.engine.gear_id+=1
		if event.type==pygame.MOUSEBUTTONUP and buttons[2]:
			if s1.engine.gear_id>0:
				s1.engine.gear_id-=1				
	time=clock.tick()	
	time=time/1000
	if s1.dead:
		print('dead')
	else:
		world.process(time)
		world.display(screen)
		
		if s1.time>=1:
			print(s1.velocity,' ',s1.distance,' ', s1.tank,' ',e1.gear_id)
			s1.time=0
	pygame.display.flip()	