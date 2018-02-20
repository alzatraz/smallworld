import numpy as np 
import random 
import math

class Work:
	def __init__(self):
		self.place = [0,0]
		self.type = 0
		self.shedule = [0,0]
	def __init__(self, place, typ, shedule):
		self.place = place
		self.type = typ
		self.shedule = shedule


class Activity_theoric:
	def __init__(self):
		self.possible_places = [(0,0)]
		self.type = 0
		self.possible_shedule = (0,0)
		self.duration = 1
	def __init__(self, place, typ , pos_sh, duration):
		self.place = place
		self.type = typ
		self.possible_shedule = pos_sh
		self.duration = duration

class Activity_real:
	def __init__(self):
		self.place = (0,0)
		self.type = 0
		self.shedule = (0,0)

	def compute_shedule(possible_shedule, duration):
		first_start = possible_shedule[0]
		last_start = min(possible_shedule[1]-duration, first_start)
		delta = last_start - first_start
		r = random.random()
		return(first_start + delta*r)

	def choose_place(l, origin):
		x = origin[0]
		y = origin[1]
		best_pos = l[0]
		bets_dist = math.sqrt((x-best_pos[0])*(x-best_pos[0])+(y-best_pos[1])*(y-best_pos[1]))
		for (a,b) in l:

	def make_real(d,p):
		self.place = choose_place(d.places, p.home)
		self.type = d.type
		self.shedule  = compute_shedule(d.possible_shedule, d.duration)


class Personn:
	def __init__(self):
		self.name = "pablo"
		self.family = []
		self.work = Work()
		self.home = [0,0]
		self.activities = []
		self.planning = []
		self.typical_travels  = []


def make_possible_activities():
	possible_activities = []
	possible_activities.append(Activity_theoric([(100,10)], "cinema", (9,22),1.5))
	possible_activities.append(Activity_theoric([(100,10)], "grosseries", (9,19),.5))
	return(possible_activities)

print(make_possible_activities())