# -*- coding: utf-8 -*-
from vector import Vector2
space_size=Vector2(780,560)
screen_size=Vector2(780,720)
unit_size=Vector2(780,620)
#energy table
Fuel={}
#{id:(power,weight)}
petrol={'#89':(20,5),'#92':(23,4.5),'#95':(25,4.2)}
Fuel['Petrol']=petrol
H2={'N2H4-C':(40,2),'H2-B':(50,1.8),'H2-A':(60,1.5)}
Fuel['Hydrogen']=H2
nuclear={'U-235':(500,10),'Pu-239':(505,10),'Th-232':(520,10)}
Fuel['Nuclear']=nuclear
