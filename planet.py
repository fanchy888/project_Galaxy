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


#*********USER************
class User(object):
	def __init__(self,data):
		self.money=10000
		self.ship=data[0]
		
		
	
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
				if cursor.x>i*self.icon_lenth and cursor.x<(i+1)*self.icon_lenth and not self.units[self.current_unit].confirm:
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
		self.confirm=False
	def display(self,surface):
		pass



class Gas_station(Unit):
	def __init__(self,user,data):
		super().__init__('Gas',user,data[0])
		self.image=data[1]
		self.energy_list=data[3]
		self.font=data[2]	
		self.position=Vector2(0,0)	
		self.current_type=0
		self.fuel_id=None
		self.confirm=False
		self.fuel=None
		self.tank_state=''
		self.total_cost=0
		self.refund=data[4]
	def check(self,cursor):
		if not self.confirm and cursor.x>50 and cursor.x<50+100:
			for i in range(len(self.energy_list)):
				if cursor.y>100+i*50 and cursor.y<100+i*50+30:
					self.current_type=i
					self.fuel_id=None
			if cursor.y>450 and cursor.y<450+30 :
				self.confirm=True
				self.tank_state='empty'
		else:
			if not self.confirm:
				if cursor.x>250 and cursor.x<250+250:
					for i in range(1,len(self.energy_list[self.current_type])):
						if cursor.y>90+(i-1)*160 and cursor.y<90+(i-1)*160+100:
							self.fuel_id=i
							self.confirm=True
							self.generate_fuel()
							break
			else:
				if self.tank_state is 'ready':
					if cursor.y>360 and cursor.y<360+25:
						if cursor.x>315 and cursor.x<315+50:
							self.confirm=False
							self.check_out()
						else:
							if cursor.x>415 and cursor.x<415+50:
								self.confirm=False
				elif self.tank_state is 'clear': 
					if cursor.y>360 and cursor.y<360+25:
						if cursor.x>365 and cursor.x<365+50:
							self.confirm=False
				elif self.tank_state is 'empty': 
					if self.user.ship.tank:
						if cursor.y>360 and cursor.y<360+25:
							if cursor.x>315 and cursor.x<315+50:
								self.confirm=False
								self.recycle()
							else:
								if cursor.x>415 and cursor.x<415+50:
									self.confirm=False	
					else:
						if cursor.y>360 and cursor.y<360+25:
							if cursor.x>365 and cursor.x<365+50:
								self.confirm=False		
				elif self.tank_state is 'match':	
					if cursor.y>360 and cursor.y<360+25:
						if cursor.x>365 and cursor.x<365+50:						
							self.confirm=False
				else:
					pass
	def generate_fuel(self):
		type=self.energy_list[self.current_type][0]
		id=self.energy_list[self.current_type][self.fuel_id][0]
		cost=self.energy_list[self.current_type][self.fuel_id][1]
		if type in self.user.ship.engine.fuel_type:
			self.fuel=Energy([(type,id),cost,commons.Fuel[type][id]])
			self.total_cost=(self.user.ship.tank_Max-self.user.ship.tank)*cost
			if self.user.ship.tank>0:
				if (type,id)==self.user.ship.fuel.type:
					self.tank_state='ready'
				else:
					self.tank_state='clear'	
			else:
				self.tank_state='ready'
		else:
			self.tank_state='match'
	def check_out(self):
		self.user.ship.add_fuel(self.fuel)
		if self.total_cost<=self.user.money:
			amount=self.user.ship.tank_Max
		else:
			amount=self.user.money/self.fuel.cost
		self.user.ship.fill_tank(amount)
		self.total_cost=min(self.total_cost,self.user.money)
		self.user.money-=self.total_cost
		self.user.ship.calculate()
	def recycle(self):
		type=self.user.ship.fuel.type[0]
		price=self.refund[type]*self.user.ship.tank
		self.user.money+=price	
		self.user.ship.tank=0
		self.user.ship.calculate()
	def display(self,surface):
		surface.blit(self.image,self.position)
		#types
		x=50
		y=100
		bar=Vector2(100,30)
		for i in range(len(self.energy_list)):
			text=self.font.render(self.energy_list[i][0],True,(255,255,255))
			if self.current_type==i:
				pygame.draw.rect(surface,(42,117,136),((x,y+4),bar))
				position=Vector2(x,y+4)+(bar-text.get_size())/2
			else:
				pygame.draw.rect(surface,(92,167,186),((x,y),bar))
				position=Vector2(x,y)+(bar-text.get_size())/2
				pygame.draw.rect(surface,(72,147,166),((x,y+30),(bar.x,4)))	
			surface.blit(text,position)
			y+=50
		y=450
		pygame.draw.rect(surface,(92,167,186),((x,y),bar))
		text=text=self.font.render('Recycle',True,(255,255,255))
		position=Vector2(x,y)+(bar-text.get_size())/2
		surface.blit(text,position)
		#id
		x=200
		y=60
		bar=Vector2(360,480)
		pygame.draw.rect(surface,(0,0,0),((x,y),bar),1)
		x=250
		y=90
		bar=Vector2(250,100)
		for i in range(1,len(self.energy_list[self.current_type])):
			pygame.draw.rect(surface,(0,0,0),(x,y,250,100),1)
			pygame.draw.rect(surface,(200,200,200),(x,y,250,100))
			id=self.energy_list[self.current_type][i][0]
			id=self.font.render(id,True,(0,0,0))
			surface.blit(id,(x,y))
			cost=str(self.energy_list[self.current_type][i][1])+'$/T'
			cost=self.font.render(cost,True,(0,0,0))
			surface.blit(cost,(x+50,y+50))
			y+=160
		#confirm window
		if self.confirm:
			bar=Vector2(300,200)
			position=(commons.unit_size-bar)/2
			pygame.draw.rect(surface,(255,255,255),(position,bar))
			pygame.draw.rect(surface,(0,0,0),(position,bar),2)
			block=Vector2(50,25)
			if self.tank_state is 'ready':
				text=str(format(min(self.total_cost,self.user.money),'0.2f'))+'$ Total?'
				text=self.font.render(text,True,(0,0,0))
				shift=position+(Vector2(300,100)-text.get_size())/2
				surface.blit(text,shift)
				text=self.font.render('Yes',True,(0,0,0))
				shift=position+Vector2(75,150)
				pygame.draw.rect(surface,(0,0,0),(shift,block),2)			
				surface.blit(text,shift+(block-Vector2(text.get_size()))/2)
				text=self.font.render('No',True,(0,0,0))
				shift=position+Vector2(175,150)
				pygame.draw.rect(surface,(0,0,0),(shift,block),2)			
				surface.blit(text,shift+(block-Vector2(text.get_size()))/2)
			elif self.tank_state is 'match':
				text='It doesn\'t fit your engine'
				text=self.font.render(text,True,(0,0,0))
				shift=position+(Vector2(300,100)-text.get_size())/2
				surface.blit(text,shift)
				text=self.font.render('Fine',True,(0,0,0))
				shift=position+Vector2(125,150)
				pygame.draw.rect(surface,(0,0,0),(shift,block),2)			
				surface.blit(text,shift+(block-Vector2(text.get_size()))/2)				
			elif self.tank_state is 'clear':
				text='Clear your tank first'
				text=self.font.render(text,True,(0,0,0))
				shift=position+(Vector2(300,100)-text.get_size())/2
				surface.blit(text,shift)
				text=self.font.render('OK',True,(0,0,0))
				shift=position+Vector2(125,150)
				pygame.draw.rect(surface,(0,0,0),(shift,block),2)			
				surface.blit(text,shift+(block-Vector2(text.get_size()))/2)		
			elif self.tank_state is 'empty':
				if self.user.ship.tank:
					type=self.user.ship.fuel.type[0]
					text='Refund '+str(format(self.refund[type]*self.user.ship.tank,'0.2f'))+'$ Total?'
					text=self.font.render(text,True,(0,0,0))
					shift=position+(Vector2(300,100)-text.get_size())/2
					surface.blit(text,shift)
					text=self.font.render('Yes',True,(0,0,0))
					shift=position+Vector2(75,150)
					pygame.draw.rect(surface,(0,0,0),(shift,block),2)			
					surface.blit(text,shift+(block-Vector2(text.get_size()))/2)
					text=self.font.render('No',True,(0,0,0))
					shift=position+Vector2(175,150)
					pygame.draw.rect(surface,(0,0,0),(shift,block),2)			
					surface.blit(text,shift+(block-Vector2(text.get_size()))/2)		
				else:
					text='Your tank is empty'
					text=self.font.render(text,True,(0,0,0))
					shift=position+(Vector2(300,100)-text.get_size())/2
					surface.blit(text,shift)
					text=self.font.render('OK',True,(0,0,0))
					shift=position+Vector2(125,150)
					pygame.draw.rect(surface,(0,0,0),(shift,block),2)			
					surface.blit(text,shift+(block-Vector2(text.get_size()))/2)	
			else:
				pass
		#user info
		x=600
		y=100
		bar=Vector2(140,100)
		position=Vector2(x,y+30)
		text=self.font.render('Fund:'+str(format(self.user.money,'0.2f')+'$'),True,(0,0,0))
		surface.blit(text,(x,70))
		text=self.font.render('Info: ',True,(0,0,0))
		surface.blit(text,(x,y))
		pygame.draw.rect(surface,(219,207,202),(position,bar))
		if self.user.ship.tank:
			text=self.font.render(self.user.ship.fuel.type[0],True,(0,0,0))
			surface.blit(text,(x+5,position.y+5))
			text=self.font.render(self.user.ship.fuel.type[1],True,(0,0,0))
			surface.blit(text,(x+5,position.y+30))
			text=self.font.render('m:'+str(format(self.user.ship.tank_weight,'0.1f')),True,(0,0,0))
			surface.blit(text,(x+5,position.y+55))
			pygame.draw.rect(surface,(166,137,124),(position+(0,80),(140,10)))
		else:
			text=self.font.render('EMPTY',True,(0,0,0))
			surface.blit(text,position+(bar-text.get_size())/2)			
		pygame.draw.rect(surface,(0,0,0),(position,bar),2)
		
		text=self.font.render('Volume(T): ',True,(0,0,0))
		surface.blit(text,(x,y+170))
		text=self.font.render(str(format(self.user.ship.tank,'0.0f'))+'/'+str(self.user.ship.tank_Max),True,(0,0,0))
		surface.blit(text,(x+(bar[0]-text.get_width())/2,y+200))
		percent=self.user.ship.tank/self.user.ship.tank_Max*150
		pygame.draw.rect(surface,(230,228,192),(x+35,y+220+150-percent,70,percent))
		pygame.draw.line(surface,(255,200,200),(x+35,y+220+150-percent),(x+35+70,y+220+150-percent),1)
		for i in range(0,25):
			if i%5:
				pygame.draw.line(surface,(0,0,0),(x+35,y+220+i*6),(x+35+6,y+220+i*6),2)
			else:
				pygame.draw.line(surface,(0,0,0),(x+35,y+220+i*6),(x+35+10,y+220+i*6),2)
		pygame.draw.rect(surface,(0,0,0),(x+35,y+220,70,150),2)
	
	
#test bench	
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
e1=Engine(s1,500,'test',gears,['Petrol','Hydrogen','Solar'])	
b1=Battery(s1,('B1',100,1000))
s1.add_battery(b1)
s1.add_engine(e1)




	
font=pygame.font.SysFont("consolas",18)		
icon=pygame.image.load('gun.png').convert_alpha()	
p1=Planet(font)
u1=User([s1])
G1=Gas_station(u1,[icon,icon,font,(('Petrol',('#89',1.1),('#92',1.3),('#95',1.5)),('Hydrogen',('N2H4-C',10),('H2-B',15)),('Nuclear',('Th-232',299),('Pu-239',269))),{'Petrol':0.9,'Hydrogen':9,'Nuclear':200}])
p1.add_unit(G1)	
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
			
	time=clock.tick()	
	time=time/1000		
	p1.display(screen)
	pygame.display.flip()				
	
			
		