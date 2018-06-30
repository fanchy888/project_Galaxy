# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from sys import exit
import random

from FSM import *
from vector import Vector2


#********Frame of ship********

class Spacecraft(object):
	def __init__(self,images,space):
		self.space=space
		self.image=images
		#self.size=Vector2(images.get_size())
		self.position=Vector2(500,330)#Vector2((space.size.x-self.size.x)/2,space.size.y)
		self.direction=Vector2(0,0)
		self.weapons={}
		self.weapon_id=0
		self.load_Max=1000
		self.load=1000
		self.engine=None #speed range, acceleration
		self.tank=1000 #current tank weight
		self.tank_Max=1000#full tank weight
		self.fuel=None #energy type and parameters
		self.shields={}
		self.shieid_id=0
		self.hp=100
		self.velocity=0
		self.speed=200
		self.distance=0
		self.time=0
		self.dead=False
		self.consume_rate=2
	def add_engine(self,engine):
		self.engine=engine
	def add_weapon(self,weapon):
		self.weapons[self.weapon_id]=weapon
		self.weapon_id+=1
	def add_shield(self,shield):
		self.shields[self.shield_id]=shield
		self.shield_id+=1
	def fill_tank(self,fuel):
		self.fuel=fuel
		self.tank=self.tank_Max
	def move(self,time):
		self.position=self.position+self.direction*time*self.speed
	def fire(self,time):
		for weapon in self.weapons.copy().values():
			weapon.process(time)	
	def consume(self,time):
		transport=self.engine.power*time
		routine=self.consume_rate*time*self.fuel.weight
		self.tank=self.tank-routine-transport
		self.load=self.tank
	def process(self,time):
		self.engine.work(time)
		self.move(time)
		self.fire(time)
		self.consume(time)
		self.check()
		
		self.distance+=self.velocity*time
		self.time+=time
	def display(self,surface):
		surface.blit(self.image,self.position)
	def check(self):	
		if self.tank<=0 or self.hp<=0:
			self.dead=True
		
#engine 		
class Engine(object):
	def __init__(self,craft,speed,name,gears,fuel_list):
		self.ship=craft
		self.name=name
		self.speed_H=speed
		self.power=0
		self.a=0
		self.gear_box=gears
		self.gear_id=1
		self.fuel_type=fuel_list
		self.acc_rate=100
		self.keep_rate=1 #lower better
	def work(self,time):
	#speed
		if self.ship.velocity<=self.speed_H: 
			self.a=self.gear_box[self.gear_id]*self.ship.fuel.power/self.ship.load*self.acc_rate #parameter
		else:
			self.a=0		
		self.ship.velocity+=self.a*time
		self.ship.velocity=min(self.ship.velocity,self.speed_H)
		self.ship.velocity=max(self.ship.velocity,0) #make sure the V is within the range
	#power			
		power_acc=abs(self.gear_box[self.gear_id])*self.ship.fuel.weight # each gear consume a constant number of fuel
		power_keep=((self.ship.velocity/100)**2)*self.keep_rate/self.ship.fuel.power*self.ship.fuel.weight #higher the speed, higher the power to keep the speed
		self.power=power_acc+power_keep
	
class Energy(object):
	def __init__(self,data):
		self.type=data[0]
		self.cost=data[1]
		self.power=data[2]
		self.weight=data[3]

class Weapon(object):
	pass
class Shield(object):
	pass
		
#********Frame of Space*********	
	
class Space(object):
	def __init__(self):
		self.background=pygame.surface.Surface((1080,720)).convert()
		self.background.fill((0,0,0))
		self.time=0
		self.chapter=None
		self.position=(0,0)
		self.panel=None
		self.ship=None
		self.enemies={}
		self.bullets={}
		self.bullet_id=0
		self.enemy_id=0
		self.FSM=FSM()
		self.stars=[]
	def reset(self):
		self.enemys={}
		self.bullets={}
		self.bullet_id=0
		self.enemy_id=0
		self.panel.reset()
	def process(self,time):
		self.time+=time
		enemys=self.enemies.copy()
		bullets=self.bullets.copy()
		if not self.ship.dead:
			if self.time%1>0.5:
				self.set_star()
			for star in self.stars:
				star.next_y=star.y+time*star.speed
			for key in enemys.keys():
				self.enemys[key].process(time)
			for key in bullets.keys():
				self.bullets[key].process(time)
			self.ship.process(time)
			#self.FSM.think()
	def display(self,surface):
		surface.blit(self.background,(0,0))
		#awesome background

		for star in self.stars:
			if self.ship.position.y<=star.y:
				G=100
				R=255
				B=100
			else:
				G=100
				B=255
				R=100
			if star.speed<=200:
				R=255
				G=255
				B=255
			pygame.draw.aaline(surface,(R,G,B),(star.x, star.next_y),(star.x, star.y-1))
			star.y=star.next_y
		
		
		
		for enemy in self.enemies.values():
			enemy.display(surface)
		for bullet in self.bullets.values():
			bullet.display(surface)
		self.ship.display(surface)		
		#self.panel.display(surface)
	def add_enemy(self,enemy):
		self.enemies[self.enemy_id]=enemy
		enemy.id=self.enemy_id
		self.enemy_id+=1
	def add_bullet(self,bullet):
		self.bullets[self.bullet_id]=bullet
		bullet.id=self.bullet_id
		self.bullet_id+=1	
	def delete_enemy(self,id):
		del self.enemies[id]
	def delete_bullet(self,id):
		del self.bullets[id]
				
	def set_universe(self,chapter):
		self.reset()
		self.chapter=chapter
		
	def set_star(self):
		x=random.randint(0,1080)
		y=0
		speed=random.randint(10,110+int(self.ship.velocity))
		self.stars.append(Star(x,y,speed))
		self.stars=list(filter(del_star,self.stars))
		
		
		
#filter function		
def del_star(star):
	return star.y<720
#stars in background 
class Star(object):
	def __init__(self,x,y,speed):
		self.x=x
		self.y=y
		self.speed=speed
		self.next_y=y

		
#***********Frame of Planet************

class Planet(object):
	pass
	