# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from sys import exit
import random
import math
from FSM import *
from vector import Vector2
import commons
from space import *
#***********Frame of Planet************

class Planet(object):
	def __init__(self,font):
		self.font=font
		self.units=[]
		self.current_unit=0
		self.size=Vector2(780,100)
		self.position=commons.screen_size-self.size
		self.icon_lenth=0
	def check(self):
		cursor=Vector2(pygame.mouse.get_pos())
		if cursor.y<720 and cursor.y>600:
			for i in range(len(self.units)):				
				if cursor.x>i*self.icon_lenth and cursor.x<(i+1)*self.icon_lenth:
					self.current_unit=i	
		else:
			self.units[self.current_unit].check(cursor)
	def process(self):
		self.units[self.current_unit].process()
	def display(self,surface):
		pygame.draw.rect(surface,(150,150,150),(self.position,self.size),5)
		pygame.draw.rect(surface,(0,0,0),(self.position,self.size),2)
		for i in range(1,len(self.units)):
			x=i*self.icon_lenth
			y=self.position.y
			pygame.draw.line(surface,(150,150,150),(x,y),(x,y+self.size.y),5)
			pygame.draw.line(surface,(0,0,0),(x,y),(x,y+self.size.y),2)
		for i in range(len(self.units)):
			x=self.position.x+i*self.icon_lenth
			y=self.position.y
			surface.blit(self.units[i].icon,(x,y))
			if self.current_unit==i:
				pygame.draw.rect(surface,(192,247,252),((x,y),(self.icon_lenth,self.size.y)),5)	
		self.units[self.current_unit].display(surface)
	def add_unit(self,unit):
		self.units.append(unit)
		self.icon_lenth=self.size.x//len(self.units)
		
		
class Unit(object):
	def __init__(self,name,user,icon):
		self.name=name
		self.id=0
		self.user=user
		self.icon=icon
	def display(self,surface):
		pass
	def process(self):
		print(self.name)


class Gas_station(Unit):
	def __init__(self,user,data):
		super().__init__('Gas',user,data[0])
		self.image=data[1]
		self.energy_list=data[3]
		self.font=data[2]	
		self.position=Vector2(0,0)	
		self.current_type=0
		self.fuel_id=''
	def check(self,cursor):
		if cursor.x>50 and cursor.x<150:
			for i in range(len(self.energy_list)):
				if cursor.y>200+i*60 and cursor.y<200+i*60+30:
					self.current_type=i
					self.fuel_id=''
		else:
			if cursor.x>200 and cursor.x<200+250:
				for i in range(1,len(self.energy_list[self.current_type])):
					if cursor.y>80+(i-1)*160 and cursor.y<80+(i-1)*160+100:
						self.fuel_id=self.energy_list[self.current_type][i]
	def display(self,surface):
		surface.blit(self.image,self.position)
		x=50
		y=200
		for i in range(len(self.energy_list)):
			pygame.draw.rect(surface,(0,0,0),(x,y,100,30),2)
			type=self.font.render(self.energy_list[i][0],True,(0,0,0))
			surface.blit(type,(x,y))
			if self.current_type==i:
				pygame.draw.rect(surface,(250,128,213),(x,y,100,30),3)
			y+=60
		x=200
		y=60
		bar=Vector2(360,480)
		pygame.draw.rect(surface,(0,0,0),((x,y),bar),1)
		x=250
		y=90
		bar=Vector2(250,100)
		for i in range(1,len(self.energy_list[self.current_type])):
			id=str(self.energy_list[self.current_type][i])
			id=self.font.render(id,True,(0,0,0))
			pygame.draw.rect(surface,(0,0,0),(x,y,250,100),1)
			pygame.draw.rect(surface,(200,200,200),(x,y,250,100))
			surface.blit(id,(x,y))
			y+=160
	def process(self):
		print(self.energy_list[self.current_type][0],self.fuel_id)





	
#test bench	
screen=pygame.display.set_mode((780,720),0,32)
pygame.display.set_caption('biu~~')	
clock=pygame.time.Clock()	
pygame.init()	
	
font=pygame.font.SysFont("consolas",18)		
icon=pygame.image.load('gun.png').convert_alpha()	
p1=Planet(font)
p1.add_unit(Gas_station(p1,[icon,icon,font,(('gas',12,13,14),('a',3,4),('n',1,2))]))	
p1.add_unit(Unit(1,p1,icon))	
p1.add_unit(Unit('asdf',p1,icon))	
while True:
	screen.fill((255,255,255))
	buttons=pygame.mouse.get_pressed()
	keys=pygame.key.get_pressed()	
	for event in pygame.event.get():	
		if event.type==QUIT:
			exit()
		if event.type==MOUSEBUTTONUP and buttons[0]:
			p1.check()
			#p1.units[p1.current_unit].check()
			
	time=clock.tick()	
	time=time/1000		
	p1.process()
	p1.display(screen)
	pygame.display.flip()				
	
			
		