# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from sys import exit
import random
import math
from FSM import *
from vector import Vector2
import commons

space_size=Vector2(780,560)
#********Frame of ship********

class Spacecraft(object):
	def __init__(self,images,space):
		self.space=space
		self.image=images
		self.size=Vector2(images.get_size())
		self.direction=Vector2(0,0)
		self.weapons=[]	
		self.weapon_max=4
		self.weapon_shift=Vector2(0,5)
		self.speed_max=200
		self.load_Max=10000 #matter
		self.load=0
		self.engine=None #speed range, acceleration
		self.battery=None #electricity power
		self.tank=0 #current tank volume
		self.tank_Max=2000#full tank volume
		self.tank_weight=0 #weight
		self.fuel=None #energy type and parameters
		self.shields=[None,None,None] # physical, electromagnetic, dark field (equipped or not)
		self.shieid_id=0					
		self.routine_power=40 #unit: power
		self.hold_breath=10 #hp decrement after out of power
		self.radius=math.sqrt(self.size*self.size)/2-5
		self.reset()
	def reset(self):		
		self.position=Vector2(self.space.size.x/2,self.space.size.y-250)
		self.speed=self.speed_max
		self.hp=100
		self.distance=0
		self.time=0	
		self.velocity=0
		self.weapon_id=0
		self.power_require=self.routine_power
		self.weapon_power=0
		self.shield_power=0
		self.power=0
		self.weapon_weight=0
		self.shield_weight=0
		#flags
		self.dead=False
		self.biu=False #fire
		self.shield_up=[False,False,False] #turn it on or not(user controls)
		self.out_of_energy=False #energy
		self.out_of_power=False #begin lose hp
		self.disable_weapon=True
		self.disable_move=False
		self.disable_shield=[True,True,True] #available or not(ship controls)
	def add_battery(self,battery):
		self.battery=battery
	def add_engine(self,engine):
		self.engine=engine
	def add_weapon(self,weapon):
		weapon.id=len(self.weapons)
		self.weapons.append(weapon)
	def add_shield(self,shield):
		self.shields[shield.type]=shield
	def add_fuel(self,fuel):
		self.fuel=fuel
	def fill_tank(self,amount):	
		if amount:
			self.tank=amount
		self.tank_weight=self.tank*self.fuel.weight
	def move(self,time):
		if self.disable_move:
			self.direction=Vector2(0,0)-self.direction
			self.speed=self.speed_max*self.power/self.routine_power
		self.position=self.position+self.direction*time*self.speed
	def breath(self,time):
		if self.out_of_power:
			self.hp-=self.hold_breath*time
		self.hp=max(0,self.hp)
	def consume(self,time):		
		transport=self.engine.power*time
		routine=self.power/self.fuel.power*time
		self.tank=max(self.tank-routine-transport,0)	
		
	def switch_on(self):		
		if self.biu and self.weapons:
			self.weapon_power=self.weapons[self.weapon_id].power
			self.disable_weapon=False
		else:
			self.disable_weapon=True
			self.weapon_power=0	
			
		self.shield_power=0
		for i in range(len(self.shields)):
			if self.shield_up[i]:
				self.shield_power+=self.shields[i].power
				self.disable_shield[i]=False
			else:
				self.disable_shield[i]=True
				
		self.power_require=self.routine_power+self.weapon_power+self.shield_power
		self.power=min(self.battery.output,self.power_require)	
		self.calculate()
	def calculate(self):
		self.tank_weight=self.tank*self.fuel.weight
		self.weapon_weight=0
		for weapon in self.weapons:
			self.weapon_weight+=weapon.weight
		self.shield_weight=0
		for shield in self.shields:
			if shield:
				self.shield_weight+=shield.weight
		self.load=self.tank_weight+self.weapon_weight+self.shield_weight
	def process(self,time):		
		self.switch_on()
		self.check()
		self.move(time)
		self.engine.work(time)			
		self.breath(time)
		if not self.disable_weapon:
			for weapon in self.weapons:
				weapon.process(time)
		for i in range(len(self.shields)):
			if not self.disable_shield[i]:
				self.shields[i].process(time)
		if not self.space.chapter.complete:
			self.battery.process(time)	
			self.consume(time)		
			self.distance+=self.velocity*time/1000
			self.distance=min(self.distance,self.space.chapter.distance)
			self.time+=time	
	def display(self,surface):	
		surface.blit(self.image,self.position-self.size/2)
		if self.weapons and not self.disable_weapon :
			self.weapons[self.weapon_id].display(surface)
		for i in range(len(self.shields)):
			if not self.disable_shield[i]:
				self.shields[i].display(surface)
	def check(self):
		if self.tank<=0:
			self.out_of_energy=True
		if self.hp<=0:
			self.dead=True
		if self.shields[0]:
			self.shield_up[0]=True	
		#power system
		if self.power<self.routine_power+self.weapon_power:
			self.disable_weapon=True
			if self.power<self.routine_power:
				self.disable_move=True
				if self.power<=0:
					self.out_of_power=True #begin dying
		if self.power<self.routine_power+self.weapon_power+self.shield_power:
			for i in range(1,len(self.shields)):
				self.disable_shield[i]=True
		#shield charging
		if self.disable_shield[1] and self.shields[1]:
			self.shields[1].hp=0
		#boundary	
		if not self.space.chapter.complete:
			if self.position.x>=self.space.size.x-self.size.x/2-10 and self.direction.x==1 \
			or self.position.x<=self.size.x/2+10 and self.direction.x==-1:
				self.direction.x=0
			if self.position.y>=self.space.panel.position.y-self.size.y/2-10 and self.direction.y==1 \
			or self.position.y<=self.size.y/2+10 and self.direction.y==-1:
				self.direction.y=0

#battery
class Battery(object):
	def __init__(self,ship,data):
		self.name=data[0]
		self.power=data[1]
		self.output=data[1]
		self.life_max=data[2]
		self.life=data[2] #times
		self.percent=100
		self.decay=5
		self.ship=ship
	def process(self,time):
		self.life-=time
		self.percent=self.life/self.life_max
		if self.ship.out_of_energy:
			self.output=self.ship.power-self.decay*time
		else:	
			self.output=self.percent*self.power
		self.output=max(0,self.output)
	def repair(self):
		self.life=self.life_max
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
		if not self.ship.out_of_energy:
			if self.ship.velocity<=self.speed_H: 
				self.a=self.gear_box[self.gear_id]*self.ship.fuel.power/self.ship.load*self.acc_rate #parameter
			else:
				self.a=0	
		else:
			self.a=-10-math.sqrt(self.ship.velocity)
		self.ship.velocity+=self.a*time
		self.ship.velocity=min(self.ship.velocity,self.speed_H)
		self.ship.velocity=max(self.ship.velocity,0) #make sure the V is within the range
	#power			
		power_acc=abs(self.gear_box[self.gear_id]) # each gear consume a constant number of fuel
		power_keep=((self.ship.velocity/100)**2)*self.keep_rate/self.ship.fuel.power #higher the speed, higher the power to keep the speed
		self.power=power_acc+power_keep
# fuel
class Energy(object):
	def __init__(self,data):
		self.type=data[0]
		self.cost=data[1] #per volume
		self.power=data[2][0] #per volume
		self.weight=data[2][1] #per volume
		
#weapons
class Weapon(object):
	def __init__(self,space,data):
		self.image=data[0]
		self.name=data[1]
		self.cd=data[2]
		self.bullet_damage=data[3]
		self.bullet_image=data[4]
		self.bullet_speed=data[5]
		self.power=data[6]
		self.icon=data[7]
		self.weight=data[8]
		self.ammo_max=data[9]
		self.ammo=data[9]
		self.time=data[2]
		self.space=space
		self.ship=space.ship
		self.ready=True
		self.fire=False
		self.position=Vector2(0,0)
		self.id=0
	def reload(self):
		self.ammo=self.ammo_max
	def display(self,surface):
		mouse_position=Vector2(pygame.mouse.get_pos())	#rotate
		face_to=mouse_position-self.position
		face_to.unit()
		angle=math.asin(face_to.x)
		angle=math.degrees(angle)-180
		if face_to.y<0:
			angle=180-angle
		image_rotate=pygame.transform.rotate(self.image,angle)
		position=self.position-Vector2(image_rotate.get_size())/2
		surface.blit(image_rotate,position)
	def move(self):
		self.position=self.ship.position+self.ship.weapon_shift
	def check(self):
		if self.time>self.cd:
			self.ready=True
		else:
			self.ready=False
	def shoot(self):
		self.fire=False
		self.time=0		
		direction=Vector2(pygame.mouse.get_pos())-self.position
		direction.unit()
		angle=math.asin(direction.x)
		angle=math.degrees(angle)-180
		if direction.y<0:
			angle=180-angle
		position=self.position+20*direction
		image_rotate=pygame.transform.rotate(self.bullet_image,angle)
		data=[image_rotate, self.bullet_speed, position, self.space, self.bullet_damage, direction]
		self.space.add_bullet(Bullet(data))		
	def process(self,time):
		self.time+=time
		self.move()
		self.check()
		if self.ready and self.fire and self.ammo:
			self.shoot()
			self.ammo-=1
#bullets		
class Bullet(object):		
	def __init__(self,data):
		self.image=data[0]
		self.speed=data[1]
		self.position=data[2]
		self.space=data[3]
		self.id=0
		self.name='biu'
		self.damage=data[4]
		self.direction=data[5]
	def move(self,time):
		self.position+=self.speed*self.direction*time
	def check(self):
		if self.position[1]<0 or self.position[1]>space_size[1]\
		or self.position[0]<0 or self.position[0]>space_size[0]:
			self.space.delete_bullet(self.id)
		else:
			self.hit()		
	def display(self,surface):
		surface.blit(self.image,self.position-Vector2(self.image.get_size())/2)	
	def process(self,time):
		self.check()
		self.move(time)
	def hit(self):
		for enemy in self.space.enemies.copy().values():
			if self.position[0]>=enemy.position[0]-enemy.image.get_width()/2 \
			and self.position[0]<=enemy.position[0]+enemy.image.get_width()/2 \
			and self.position[1]<=enemy.position[1]+enemy.image.get_height()/2 \
			and self.position[1]>=enemy.position[1]-enemy.image.get_height()/2:
				self.space.delete_bullet(self.id)
				self.space.enemies[enemy.id].hp=max(0,self.space.enemies[enemy.id].hp-self.damage)
				break			
#shield		
class Shield(object):
	def __init__(self,ship,data):
		self.ship=ship
		self.radius=0
		self.image=data[0]
		self.type=data[1]
		self.weight=data[2]
		self.hp_max=data[3]
		self.hp=data[3]
		self.effect=data[4] #0~1
		self.power=data[5]
		self.ready=True #available for attack
		if self.type==1:
			self.charge=data[6]/100 #percent per second 
			self.icon=data[7]
			self.radius=(self.image.get_width()+self.image.get_height())/4			
	def display(self,surface):		
		x=int(self.ship.position.x)
		y=int(self.ship.position.y)
		if self.type==0:
			pygame.draw.circle(surface,(255,255,255),(x,y),int(self.ship.radius),1)
		else:
			if int(self.hp/self.hp_max*100)%4<2:
				position=self.ship.position-Vector2(self.image.get_size())/2
				surface.blit(self.image,position)
	def process(self,time):
		if self.type==1:
			if self.hp<self.hp_max:
				self.ready=False
				self.hp+=self.charge*self.hp_max*time	
			else:
				self.ready=True
		elif self.type==0:
			if self.hp<=0:
				self.ready=False
			else:
				self.ready=True
		self.hp=min(self.hp,self.hp_max)
		self.hp=max(self.hp,0)
		
#********Frame of Space*********	
	
class Space(object):
	def __init__(self):
		self.background=pygame.surface.Surface((780,720)).convert()
		self.background.fill((0,0,0))
		self.time=0
		self.size=Vector2(780,720)
		self.chapter=None
		self.position=(0,0)
		self.panel=None
		self.ship=None
		self.enemies={}
		self.bullets={}
		self.bullet_id=0
		self.enemy_id=0
		self.FSM=FSM()
		self.FSM.add_state(Gameover(self))
		self.FSM.add_state(Complete(self))
		self.FSM.add_state(Begin(self))
		self.stars=[]
	def reset(self):
		self.time=0
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
			if random.randint(0,3)==1:
				self.set_star()
			for star in self.stars:
				star.next_y=star.y+time*star.speed
			for key in enemys.keys():
				self.enemies[key].process(time)
			for key in bullets.keys():
				self.bullets[key].process(time)
			self.ship.process(time)
			self.chapter.process(time)
		self.FSM.think()
		if self.chapter.complete:
			self.panel.move(time)
	def display(self,surface):
		surface.blit(self.background,(0,0))
		#awesome background
		for star in self.stars:
			if self.ship.position.y<=star.y:
				G=150
				R=255
				B=150
			else:
				G=150
				B=255
				R=150
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
		self.panel.display(surface)
	def add_panel(self,panel):
		self.panel=panel
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
		self.FSM.change_state('Begin')
	def set_star(self):
		x=random.randint(0,self.size.x)
		y=0
		speed=random.randint(10,110+int(self.ship.velocity))
		self.stars.append(Star(x,y,speed))
		self.stars=list(filter(self.del_star,self.stars))		
	#filter function		
	def del_star(self,star):
		return star.y<min(self.size.y,self.panel.position.y)
#stars in background 
class Star(object):
	def __init__(self,x,y,speed):
		self.x=x
		self.y=y
		self.speed=speed
		self.next_y=y

#FSM states
class Begin(State):
	def __init__(self,space):
		super().__init__('Begin')
		self.space=space
	def check(self):
		if self.space.chapter.complete:
			return 'Complete'
		else:
			return 'Begin'
	def start(self):
		self.space.reset()
class Complete(State):
	def __init__(self,space):
		super().__init__('Complete')
		self.space=space
	def start(self):
		self.space.reset()
	def check(self):
		if self.space.time<=3:
			return 'Gameover'
		else:
			return 'Complete'
	def run(self):
		self.space.ship.biu=False
		self.space.ship.shield_up[1]=False
		self.space.ship.speed+=0.5
		self.space.panel.speed=50
		if self.space.ship.position.y>-self.space.ship.size[1]:
			self.space.ship.direction=Vector2(0,-1)
		else:
			self.space.ship.direction=Vector2(0,0)
			print(self.space.ship.direction)
class Gameover(State):
	def __init__(self,space):
		super().__init__('Gameover')
		self.space=space	
#Panel
class Panel(object):
	def __init__(self,space,font):
		self.space=space
		self.size=Vector2(780,160)
		self.position=space.size-self.size
		self.background=pygame.surface.Surface(self.size).convert()
		self.background.fill((245,245,235))
		self.speed=0
		self.font=font
	def reset(self):
		self.position=self.space.size-self.size
		self.speed=0
	def move(self,time):
		if self.position.y<self.space.size.y:
			self.position+=self.speed*Vector2(0,1)*time
	def display(self,surface):
		surface.blit(self.background,self.position)
		pygame.draw.rect(surface,(150,150,150),(self.position,self.size),5)

		#gear		
		num=len(self.space.ship.engine.gear_box)
		id=self.space.ship.engine.gear_id
		bar=(20,110)
		x=30
		y=int(self.position.y)+30
		pygame.draw.rect(surface,(160,238,225),((x,y),bar),0)
		for i in range(num):
			y=int(self.position.y)+130-90/(num-1)*i
			pygame.draw.rect(surface,(0,0,0),((x+5,y),(10,2)),1)
			if id==i:
				pygame.draw.rect(surface,(150,102,73),((x-5,y-3),(30,6)),0)		
		if id<1: # 3 level
			info='R'
		elif id==1:
			info='N'
		else:
			info='A'+str(id-1)
		Gear=self.font.render('Gear: '+info,True,(0,0,0))
		surface.blit(Gear,self.position+(5,5))
		#tank
		x=130
		y=int(self.position.y)+30
		percent=self.space.ship.tank/self.space.ship.tank_Max*100
		bar_back=(100,20)
		bar_fill=(percent,20)
		pygame.draw.rect(surface,(230,228,192),((x,y),bar_fill),0)
		pygame.draw.rect(surface,(0,0,0),((x,y),bar_back),2)
		Text=self.font.render('Tank:',True,(0,0,0))
		percent=self.font.render('%'+str(format(percent,'0.1f')),True,(0,0,0))
		surface.blit(Text,(x-Text.get_width(),y))
		surface.blit(percent,(x+50-percent.get_width()/2,y+1))
		#battery system
		x=130
		y=int(self.position.y)+60
		percent=self.space.ship.power/self.space.ship.battery.power*100
		bar_fill=(percent,20)
		lock=100-self.space.ship.battery.percent*100
		bar_shade=(lock,20)
		pygame.draw.rect(surface,(150,150,150),((x+100-lock,y),bar_shade),0)
		pygame.draw.rect(surface,(192,247,252),((x,y),bar_fill),0)
		pygame.draw.rect(surface,(0,0,0),((x,y),bar_back),2)
		Text=self.font.render('Power:',True,(0,0,0))
		percent=self.font.render('%'+str(format(percent,'0.1f')),True,(0,0,0))
		surface.blit(Text,(x-Text.get_width(),y))
		surface.blit(percent,(x+50-percent.get_width()/2,y+1))	
		#hp
		x=130
		y=int(self.position.y)+90
		percent=self.space.ship.hp
		bar_fill=(percent,20)
		pygame.draw.rect(surface,(255,176,168),((x,y),bar_fill),0)
		pygame.draw.rect(surface,(0,0,0),((x,y),bar_back),2)
		Text=self.font.render('HP:',True,(0,0,0))
		percent=self.font.render('%'+str(format(percent,'0.1f')),True,(0,0,0))
		surface.blit(Text,(x-Text.get_width(),y))
		surface.blit(percent,(x+50-percent.get_width()/2,y+1))
		#armor:shield[0]
		if self.space.ship.shield_up[0]:
			x=130
			y=int(self.position.y)+120
			percent=self.space.ship.shields[0].hp/self.space.ship.shields[0].hp_max*100
			bar_fill=(percent,20)
			pygame.draw.rect(surface,(172,248,211),((x,y),bar_fill),0)
			pygame.draw.rect(surface,(0,0,0),((x,y),bar_back),2)
			Text=self.font.render('Armor:',True,(0,0,0))
			percent=self.font.render('%'+str(format(percent,'0.1f')),True,(0,0,0))
			surface.blit(Text,(x-Text.get_width(),y))
			surface.blit(percent,(x+50-percent.get_width()/2,y+1))
		#weapons
		x=260
		y=int(self.position.y)+5
		if not self.space.ship.disable_weapon:
			weapon_name=self.space.ship.weapons[self.space.ship.weapon_id].name
			ammo=self.space.ship.weapons[self.space.ship.weapon_id].ammo
			Text=self.font.render('Ammo:'+str(ammo),True,(0,0,0))
			surface.blit(Text,(x,y+62))
		else:
			weapon_name='Locked'
		Text=self.font.render('Weapon:'+weapon_name,True,(0,0,0))
		surface.blit(Text,(x,y))
		bar=(40,40)		
		for id in range(self.space.ship.weapon_max):	#cool down effect
			if id<len(self.space.ship.weapons):
				color=(200,200,200)
				if id==self.space.ship.weapon_id and self.space.ship.biu:
					if not self.space.ship.disable_weapon:
						color=(255,255,255)
					pygame.draw.rect(surface,(240,230,140),((x-3,y+17),bar+Vector2(6,6)),5)				
				if self.space.ship.weapons[id].time<self.space.ship.weapons[id].cd:
					O2=(x+20,y+40)
					O1=(x+20,y+20)
					TR=(x+40,y+20)
					BR=(x+40,y+60)
					BL=(x,y+60)
					TL=(x,y+20)
					percent=self.space.ship.weapons[id].time/self.space.ship.weapons[id].cd
					angle=percent*math.pi*2
					if percent<0.125:
						point=(x+20+20*math.tan(angle),y+20)
						point_list=(O1,O2,point,TR,BR,BL,TL)
					elif percent<0.375:
						point=(x+40,y+20+20*(1-1/math.tan(angle)))
						point_list=(O1,O2,point,BR,BL,TL)
					elif percent<0.625:
						point=(x+20-20*math.tan(angle),y+60)
						point_list=(O1,O2,point,BL,TL)		
					elif percent<0.875:
						point=(x,y+40+20/math.tan(angle))
						point_list=(O1,O2,point,TL)
					else:
						point=(x+20+20*math.tan(angle),y+20)
						point_list=(O1,O2,point)
					pygame.draw.rect(surface,(200,200,200),((x,y+20),bar),0)
					surface.blit(self.space.ship.weapons[id].icon,(x,y+20))
					pygame.draw.polygon(surface,(224,255,255),point_list)
				else:
					pygame.draw.rect(surface,color,((x,y+20),bar),0)
					surface.blit(self.space.ship.weapons[id].icon,(x,y+20))					
				pygame.draw.rect(surface,(0,0,0),((x,y+20),bar),2)
			else:
				color=(255,255,255)				
				pygame.draw.rect(surface,color,((x,y+20),bar),0)
				pygame.draw.rect(surface,(0,0,0),((x,y+20),bar),2)
				pygame.draw.circle(surface,(255,0,0),(x+20,y+40),18,4)
				pygame.draw.line(surface,(255,0,0),(x+10,y+30),(x+30,y+50),5)
			x+=60		
		
		#shields
		x=290
		y=int(self.position.y)+85		
			#label
		Text=self.font.render('Shield:',True,(0,0,0))
		if self.space.ship.shields[1]:
			if self.space.ship.shield_up[1] and not self.space.ship.disable_shield[1]:				
				percent=self.space.ship.shields[1].hp/self.space.ship.shields[1].hp_max*100
				bar=(100,15)
				bar_fill=(percent,15)
				pygame.draw.rect(surface,(148,251,240),((x+70,y),bar_fill),0)
				pygame.draw.rect(surface,(0,0,0),((x+70,y),bar),1)
			else:
				if self.space.ship.shield_up[1]:
					Text=self.font.render('Shield:Charging...',True,(0,0,0))
				else:
					Text=self.font.render('Shield:OFF',True,(0,0,0))
		else:
			Text=self.font.render('Shield:Unequipped',True,(0,0,0))
		surface.blit(Text,(x,y))
			#icon
		box=(40,40)
		for i in range(1,len(self.space.ship.shields)):
			if self.space.ship.shields[i]:
				if self.space.ship.shield_up[i] and not self.space.ship.disable_shield[i]:
					pygame.draw.rect(surface,(255,255,255),((x,y+20),box),0)
					pygame.draw.rect(surface,(255,255,100),((x,y+20),box),4)
				else:
					pygame.draw.rect(surface,(200,200,200),((x,y+20),box),0)	
				surface.blit(self.space.ship.shields[i].icon,(x,y+20))
			else: # disabled
				color=(255,255,255)
				pygame.draw.rect(surface,color,((x,y+20),box),0)
				pygame.draw.circle(surface,(255,0,0),(x+20,y+40),18,4)
				pygame.draw.line(surface,(255,0,0),(x+20-10,y+40-10),(x+20+10,y+40+10),5)
			pygame.draw.rect(surface,(150,150,150),((x,y+20),box),3)
			pygame.draw.rect(surface,(220,220,220),((x,y+20),box),2)
			x+=85	
		#speed
		x=505
		y=int(self.position.y)+10
		v=format(self.space.ship.velocity,'0.1f')
		Speed=self.font.render(str(v),True,(172,248,211),1)		
		Text=self.font.render('Speed:',True,(0,0,0),1)
		bar=Vector2(120,120)
		r=bar/2
		o=Vector2(x+65,y+75)
		pygame.draw.circle(surface,(172,248,211),o,20,0)
		pygame.draw.circle(surface,(231,202,127),o,5,0)
		pygame.draw.circle(surface,(142,229,213),o,20,3)
		pygame.draw.arc(surface,(172,248,211),(o-r,bar),-math.pi/6,math.pi*7/6,20)
		pygame.draw.arc(surface,(35,205,182),(o-r,bar),-math.pi/6,math.pi*7/6,1)
		angle=math.pi*7/6-self.space.ship.velocity/self.space.ship.engine.speed_H*math.pi*4/3		
		pygame.draw.line(surface,(231,202,127),o,o+50*Vector2(math.cos(angle),-math.sin(angle)),3)
		for i in range(2,100,2):
			angle=math.pi*7/6-i*2.4*math.pi/180
			s=o+59*Vector2(math.cos(angle),-math.sin(angle))			
			if i%20==0:
				e=o+50*Vector2(math.cos(angle),-math.sin(angle))
			elif i%10==0:
				e=o+53*Vector2(math.cos(angle),-math.sin(angle))
			else:
				e=o+55*Vector2(math.cos(angle),-math.sin(angle))
			pygame.draw.aaline(surface,(35,205,182),s,e,1)
		bar2=Vector2(70,24)
		x2=o.x-bar2.x/2
		y2=y+110
		pygame.draw.rect(surface,(150,150,150),((x2,y2),bar2),0)
		surface.blit(Text,(x2-Text.get_width(),y2+2))
		surface.blit(Speed,(x2+(bar2.x-Speed.get_width())/2,y2+(bar2.y-Speed.get_height())/2))
		#distance remain
		x=760
		y=int(self.position.y)+5
		distance_remain=format(max(0,self.space.ship.distance),'0.1f')
		Distance=self.font.render('Mileage:'+str(distance_remain),True,(0,0,0))
		surface.blit(Distance,(x-Distance.get_width(),y))	
		bar=(30,100)
		percent=100-self.space.ship.distance/self.space.chapter.distance*100
		pygame.draw.rect(surface,(255,215,187),((x-80,y+25),bar),0)
		pygame.draw.rect(surface,(0,0,0),((x-80,y+25),(3,100)),0)
		for i in range(5):
			pygame.draw.line(surface,(0,0,0),(x-80,y+25+i*25),(x-70,y+25+i*25),1)
		pygame.draw.polygon(surface,(255,76,108),((x-70,y+25+percent),(x-55,y+30+percent),(x-55,y+20+percent)))
		#time
		time=format(self.space.time,'0.0f')
		Speed=self.font.render('Time:'+str(time),True,(0,0,0))
		surface.blit(Speed,self.position+(700,133))			

		
#***********Frame of chapter***********	

class Chapter(object):
	def __init__(self,space,data):
		self.space=space
		self.ship=space.ship
		self.distance=data[0] 
		self.type=data[1] #rock,army,boss/ difficulty
		self.difficulty=data[2]
		self.enemy_list=data[3] #enemy_images
		self.reset()
	def reset(self): #set difficulty
		self.time=0
		self.begin=False
		self.encounter=False
		self.num=len(self.enemy_list)-1
		self.start_flag=self.distance/(self.difficulty+10)#percent 0~1
		self.cd=20/((self.difficulty+1)**2) #x seconds
		self.ecp=random.random()*self.cd # the point that encounter enemy 
		self.hp=self.difficulty**2*20
		self.speed=100+self.difficulty*20
		self.complete=False
	def check(self):
		if not self.begin and self.ship.distance>self.start_flag:
			self.begin=True
		if self.time>=self.cd: 
			self.ecp=random.random()*self.cd
			self.time=0	
			self.encounter=False
		if self.ship.distance>=self.distance:
			self.complete=True
		else:
			self.complete=False
	def process(self,time):
		self.check()
		if self.begin:
			self.time+=time
		if not self.encounter and self.time>=self.ecp:
			self.generate_enemy()
			self.encounter=True
			
	def generate_enemy(self):
		if self.difficulty:
			id=random.randint(0,self.num)
			image=self.enemy_list[id]
			hp=self.hp+random.randint(0,50)
			a=random.randint(0,5)
			position=Vector2(0,0)
			if a==0:
				position.x=-image.get_width()/2
				position.y=random.randint(0,space_size.y-200)
				direction=Vector2(1,random.random())
			elif a==1:
				position.x=space_size.x+image.get_width()/2
				position.y=random.randint(0,space_size.y-200)
				direction=Vector2(-1,random.random())
			else:	
				position.x=random.randint(image.get_width()/2,space_size.x-image.get_width()/2)
				position.y=-image.get_height()/2
				direction=Vector2(random.uniform(-0.5,0.5),1)				
			speed=self.speed+random.randint(0,20)
			data=[image,hp,position,speed,direction,0,0]
			self.space.add_enemy(Enemy(self.space,data))


class Enemy(object):
	def __init__(self,space,data):
		self.name='enemy'
		self.space=space
		self.data=data
		self.id=0
		self.target=self.space.ship
		self.image=data[0]
		self.hp=data[1]
		self.position=data[2]
		self.speed=data[3]
		self.direction=data[4]
		self.damage=data[5]
		self.bonus=data[6]		
		self.hit=0
		self.size=Vector2(self.image.get_size())/2 #for convenient
	def display(self,surface):
		surface.blit(self.image,self.position-self.size)
	def move(self,time):
		speed=self.speed+self.target.velocity/10
		self.position+=time*Vector2(self.direction.x*self.speed,self.direction.y*speed)
	def check(self):
		#boundary
		if (self.position[0]-self.size.x>=space_size.x and self.direction.x>0) \
		or (self.position[0]+self.size.x<=0 and self.direction.x<0) \
		or (self.position[1]-self.size.y>=space_size.y and self.direction.y>0):
			self.hp=0
		if self.hp<=0:
			self.space.delete_enemy(self.id)
		self.hit=0.5*self.hp*((self.speed+self.target.velocity/10)/100)**2			
	def collide(self):
		distance=(self.position-self.target.position).get_mag()	
		if self.target.shield_up[1] and self.target.shields[1].ready:
			if distance<self.target.shields[1].radius:
				self.hp-=self.target.shields[1].hp
				self.target.shields[1].hp-=self.hit
		if distance<self.target.radius:
			if self.target.shield_up[0] and self.target.shields[0].ready:
				self.hp=0
				self.target.shields[0].hp-=self.hit*self.target.shields[0].effect
				self.target.hp-=self.hit*(1-self.target.shields[0].effect)	
			else:
				self.target.hp-=self.hit
	def process(self,time):
		self.check()
		self.move(time)
		self.collide()
		


		



