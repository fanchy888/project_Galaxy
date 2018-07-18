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
	def __init__(self,user):
		self.user=user