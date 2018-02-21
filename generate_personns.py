import numpy as np 
import random 
import math


############ global variables ###############
nb_of_days = 14
p_outing_work = .1
p_outing_not_work = .5
#############################################

def distance(p1,p2):
	return(math.sqrt( (p1[0]-p2[0])*(p1[0]-p2[0])+(p1[1]-p2[1])*(p1[1]-p2[1])))


def compute_shedule(possible_shedule, duration, day, planning):
		if len(planning[day])==0:
			first_start = possible_shedule[0]
		else:
			first_start = max(possible_shedule[0],planning[day][-1][1])
		last_start = min(possible_shedule[1]-duration, first_start)
		delta = last_start - first_start
		r = random.random()
		return((first_start + delta*r),(first_start + delta*r)+duration) 

def choose_place(possible_places, origin):
		best_pos = possible_places[0]
		best_dist = distance(origin, best_pos)
		for pos in possible_places:
			new_dist = distance(origin, pos)
			if new_dist<best_dist:
				best_dist = new_dist
				best_pos = pos
		return(best_pos)

class Deplacement:
	def __init__(self):
		self.start = (0,0)
		self.end = (0,0)
		self.day = 0
		self.hour = 0
		self.tag = "none"

	def __init__(self, start, end, day, hour ):
		self.start = start
		self.end = end
		self.day = day
		self.hour = hour
		self.tag = "none"

	def __init__(self, start, end, day, hour ,tag):
		self.start = start
		self.end = end
		self.day = day
		self.hour = hour
		self.tag = tag

	def print_d(self):
		print(self.start,self.end,self.day,self.hour,self.tag)


	
class Work:
	def __init__(self):
		self.type = 0
		self.shedule = (0,0)
		self.days_worked = [True, True, True, True, True, False, False ]
	def __init__(self, typ, shedule,days_worked):
		self.type = typ
		self.shedule = shedule
		self.days_worked = days_worked


class Activity_theoric:
	def __init__(self):
		self.possible_places = [(0,0)]
		self.type = 0
		self.possible_shedule = (0,0)
		self.duration = 1
	def __init__(self, places, typ , pos_sh, duration):
		self.possible_places = places
		self.type = typ
		self.possible_shedule = pos_sh
		self.duration = duration

class Activity_real:
	def __init__(self):
		self.place = (0,0)
		self.type = 0
		self.shedule = (0,0)

	def __init__(self,act,p,day):
		self.place = choose_place(act.possible_places, p.home)
		self.type = act.type
		self.shedule  = compute_shedule(act.possible_shedule, act.duration,day, p.planning)


class Personn:
	def __init__(self):
		self.name = "pablo"
		self.family = []
		self.work = Work()
		self.age = 0
		self.home = (0,0)
		self.work_place = (0,0)
		self.activities = []
		self.planning = {}
		self.travels  = []

	def __init__(self,age,home,work,activities):
		self.name = "pablo"
		self.family = []
		self.work = work
		self.work_place = (0,0)
		self.age = age
		self.home = home
		self.activities = activities
		self.planning = []
		self.travels  = []
	
	def set_age(age):
		self.age = age

	def set_work(work):
		self.work = work
	
	def set_home(home):
		self.home = home

	def set_activities(activities):
		self.activities =activities

	def add_activity(activity):
		self.activities.append(activity)

	def is_working(self,d):
		return(self.work.days_worked[d%7])


	def add_job(self):
		for d in range(nb_of_days):
			if self.is_working(d):
				self.planning.append([(self.work_place,self.work.shedule[0]+(.5+random.random()),self.work.shedule[1]+(.5+random.random()),"work")])
			else:
				self.planning.append([])

	def random_activity(self):
		return(random.choice(self.activities))


	def add_activities(self):
		for d in range(nb_of_days):
			r = random.random()
			if self.is_working(d):
				if(r<p_outing_work):
					a = self.random_activity()
					a_real = Activity_real(a,self,d)
					self.planning[d].append( (a_real.place, a_real.shedule[0], a_real.shedule[1], a_real.type )  )

			else:
				if(r<p_outing_not_work):
					a = self.random_activity()
					a_real = Activity_real(a,self,d)
					self.planning[d].append( (a_real.place, a_real.shedule[0], a_real.shedule[1] , a_real.type )  )				




	def compute_deplacement(self):
		for day in range(nb_of_days):
			to_do = self.planning[day]
			act_loc = self.home
			for (loc , start, end,tag) in to_do:
				d1 = Deplacement(act_loc , loc ,day, start,tag)
				act_loc = loc
				self.travels.append(d1)
			if(act_loc!=self.home):
				d1 = Deplacement(act_loc , self.home ,day, end,"rentrer maison")
				self.travels.append(d1)


#################################################


def make_possible_activities_manual():
	possible_activities = []
	possible_activities.append(Activity_theoric([(100,10)], "cinema", (9,22),1.5))
	possible_activities.append(Activity_theoric([(100,10)], "grosseries", (9,19),.5))
	return(possible_activities)

######################## lets do tests #######################


################# typical working type #######################################
work_no_work = Work("no work", (0,0) ,[False, False, False, False	, False, False, False ] )
work_white_collar = Work("white collar", (9,19) ,[True, True, True, True, True, False, False ] )
work_student = Work("school", (8,17) ,[True, True, False, True, True, False, False ] )

################# typical activities #####################################
act_cinema  = Activity_theoric([(100,10)], "cinema", (9,22),1.5)
act_balade  = Activity_theoric([(100,10)], "balade", (9,19),1)
act_sport  = Activity_theoric([(100,10)], "sport", (9,19),1)
act_grosseries = Activity_theoric([(100,10)], "grosseries", (9,19),.5)

act = [act_cinema, act_balade, act_sport]

nb_test = 100000
for i in range(nb_test):
	if 100*i%(nb_test)==0:
		print(100*i/(nb_test))
	person_student = Personn(12,  (5,5), work_student, act)
	person_student.add_job()
	person_student.add_activities()
	person_student.compute_deplacement()


for d in person_student.travels:
	d.print_d()

