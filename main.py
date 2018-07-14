# -*- coding: utf-8 -*-
from vector import Vector2
import pygame
from pygame.locals import *
from sys import exit
import random
from entities import *
		
		
screen=pygame.display.set_mode((780,720),0,32)
pygame.display.set_caption('biu~~')	
clock=pygame.time.Clock()	
pygame.init()
	
ship=pygame.image.load('ship.png').convert_alpha()	

panel_font=pygame.font.SysFont("consolas",18)
gears=[-1,0,2,4,10]	
world=Space()
panel=Panel(world,panel_font)
world.add_panel(panel)
s1=Spacecraft(ship,world)
e1=Engine(s1,500,'test',gears,['gas,nuclear,solar'])	
b1=Battery(s1,('B1',100,1000))
s1.add_battery(b1)
s1.add_engine(e1)
f1=Energy(['gas',1,20,1])	
s1.add_fuel(f1)
world.ship=s1

gun=pygame.image.load('gun.png').convert_alpha()	
gun_icon=pygame.image.load('gun_icon.png').convert_alpha()	
bullet=pygame.image.load('bullet.png').convert_alpha()
gun2=pygame.image.load('gun2.png').convert_alpha()	
gun2_icon=pygame.image.load('gun2_icon.png').convert_alpha()	
bullet2=pygame.image.load('bullet2.png').convert_alpha()	

gun1_data=[gun,'machine gun',0.2,1,bullet,1000,10,gun_icon,50,100]
gun2_data=[gun2,'Canon',3,50,bullet2,500,20,gun2_icon,50,50]
gun1=Weapon(world,gun1_data)
gun2=Weapon(world,gun2_data)
s1.add_weapon(gun1)
s1.add_weapon(gun2)

shield1=pygame.image.load('shield.png').convert_alpha()	
shield_icon=pygame.image.load('shield_icon.png').convert_alpha()	
shield_data=[None,0,200,100,0.6,0]
shield=Shield(s1,shield_data)
s1.add_shield(shield)
shield_data=[shield1,1,5,1000,1,20,10,shield_icon]
shield=Shield(s1,shield_data)
s1.add_shield(shield)
shield_data=[shield1,2,5,100,1,20]
shield=Shield(s1,shield_data)
#s1.add_shield(shield)
rock=pygame.image.load('rock.png').convert_alpha()
chap_data=[100,'rock',0,[rock]]
chap_test=Chapter(world,chap_data)
world.set_universe(chap_test)
while True:
	screen.fill((200,255,255))
	buttons=pygame.mouse.get_pressed()
	keys=pygame.key.get_pressed()	
	for event in pygame.event.get():	
		if event.type==QUIT:
			exit()
		if event.type==KEYUP: 
			if event.key==K_LSHIFT:
				if s1.engine.gear_id<len(s1.engine.gear_box)-1:
					s1.engine.gear_id+=1
			if event.key==K_LCTRL:
				if s1.engine.gear_id>0:
					s1.engine.gear_id-=1
			if event.key==K_q:
				s1.biu=~s1.biu
			if event.key==K_e and s1.shields[1]:
				s1.shield_up[1]=~s1.shield_up[1]
			if event.key==K_r and s1.shields[2]:
				s1.shield_up[2]=~s1.shield_up[2]
		if event.type==MOUSEBUTTONUP:
			if event.button==4:
				s1.weapon_id+=1
			if event.button==5:
				s1.weapon_id-=1
			if event.button==3:
				world.add_enemy(Enemy(world,[rock,50,Vector2(350,0),100,Vector2(0,1),0,0]))

	if s1.weapons and s1.biu:
		s1.weapon_id=s1.weapon_id%len(s1.weapons)
		if buttons[0]:
			s1.weapons[s1.weapon_id].fire=True
		else:
			s1.weapons[s1.weapon_id].fire=False
	s1.direction*=0
	if keys[K_a] and not keys[K_d]:
		s1.direction.x=-1
	if keys[K_d] and not keys[K_a]:
		s1.direction.x=1
	if keys[K_w] and not keys[K_s]:
		s1.direction.y=-1
	if keys[K_s] and not keys[K_w]:
		s1.direction.y=1

	time=clock.tick()	
	time=time/1000

		
	world.process(time)
	world.display(screen)
	pygame.display.flip()	
'''	
	if s1.time>=1:
		print(s1.velocity,' ',s1.distance,' ', s1.tank,' ',e1.gear_id)
		s1.time=0
'''	