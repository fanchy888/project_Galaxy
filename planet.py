# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from sys import exit
import random
import math
from FSM import *
from vector import Vector2

#***********Frame of Planet************

class Planet(object):
	def __init__(self,user,data):
		self.user=user
		self.data=data
		self.units={}
		self.current_unit='Planet'
	def process(self,time):
		self.check()
		self.units[self.current_id].process(time)
	def display(self,surface):
		surface.blit(self.background,(0,0))
		self.units[self.current_unit].display(surface)
		