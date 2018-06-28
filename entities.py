# -*- coding: utf-8 -*-
from vector import Vector2
import pygame
from pygame.locals import *
from sys import exit
import random


class Spacecraft(object):
	def __init__(self,images,space):
		self.space=space
		self.image=images
		self.size=Vector2(images.get_size())
		self.position=Vector2((space.size.x-self.size.x)/2,space.size.y)
		self.direction=Vector2(0,0)
		self.weapons={}
		self.weapon_id=0
		self.max_load=1000
		self.current_load=0
		self.engine=None #speed range, acceleration, fuel consumption, 
		self.tank= #full volume 
		self.shields=0
		self.shiedle_id=0
		self.hp=100
		self.velocity=0
		self.speed=200
		self.distance=0
	def add_engine(self,engine):
		self.engine=engine
		self.velocity=engine.speed_L
	def add_weapon(self,weapon):
		self.weapons[self.weapon_id]=weapon
		self.weapon_id+=1
	def add_shield(self, shield):
		self.shields[self.shield_id]=shield
		self.shield_id+=1
	def move(self,time):
		self.position=self.position+self.direction*time*self.speed
	def fire(self,time):
		for weapon in self.weapons.values().copy():
			weapon.process(time_tick)	
	def consume(self,time):
		self.engine.rate
	def process(self,time):
		time_tick=time/1000.0
		self.engine.process(time_tick)
		self.move(time_tick)
		self.Fire(time_tick)
		self.distance+=self.velocity*time
	def display(self,surface):
		surface.blit(self.image,self.position)
		
		
class Engine(object):
	def __init__(self,craft,data,name):
		self.ship=craft
		self.name=name
		self.speed_L=data[0]
		self.speed_H=data[1]
		self.gears=data[2] #accelerations: 0:brake, 1:keep, 2-:speed up 
		self.power=0
		self.gear_id=1
	def process(self,time):
		if self.ship.velocity<=self.speed_H and self.ship.velocity>=self.speed_L:
			self.ship.velocity+=self.gears[self.gear_id]*time
		self.power=self.gears[gear_id]*
	
	
	
	
	
	
		
		