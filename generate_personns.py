import numpy as np 
import random 
import math

 


############ global variables ###############

pi = 3.14159265359 

nb_of_days = 7
p_outing_work = .15
p_outing_not_work = .6

r_center_paris = 3000
max_r = 10000
p_live_center = .1
p_work_center = .8

density_cinema_center = 97/105.1
density_cinema_outer = .2

density_sport_center = .5
density_sport_outer = .5

density_grosseries_center = .5
density_grosseries_outer = .5



################# basic fonctions ##################

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

######################### main classes #######################

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
		print(self.day,self.hour,self.start,self.end,self.tag)


	
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

	def __init__(self,age,home,work_place,work,activities):
		self.name = "pablo"
		self.work = work
		self.work_place = work_place
		self.age = age
		self.home = home
		self.activities = activities
		self.planning = []
		self.travels  = []
		self.family = []
		

	def print_p(self):
		print( self.work_place, self.home)

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



############### localisation choice ##################


def random_home_location():
	if random.random()<p_live_center:
		theta = random.random()*pi*2
		r = random.random()*r_center_paris
		x = r*math.cos(theta)
		y = r*math.sin(theta)
	else:
		theta = random.random()*pi*2
		r = random.random()*(max_r-r_center_paris)+r_center_paris
		x = r*math.cos(theta)
		y = r*math.sin(theta)
	return((x,y))


def random_work_location():
	if random.random()<p_work_center:
		theta = random.random()*pi*2
		r = random.random()*r_center_paris
		x = r*math.cos(theta)
		y = r*math.sin(theta)
	else:
		theta = random.random()*pi*2
		r = random.random()*(max_r-r_center_paris)+r_center_paris
		x = r*math.cos(theta)
		y = r*math.sin(theta)
	return((x,y))


def random_in_area(pos, radius):
	theta = random.random()*pi*2
	r = random.random()*radius
	x = pos[0]+r*math.cos(theta)
	y = pos[1]+r*math.sin(theta)
	return((x,y))

###################### localisation of activities ##########################

 ################# generating typical types ###############################

################# typical working type #######################################
work_no_work = Work("no work", (0,0) ,[False, False, False, False	, False, False, False ] )
work_white_collar = Work("white collar", (9,19) ,[True, True, True, True, True, False, False ] )
work_student = Work("school", (8,17) ,[True, True, False, True, True, False, False ] )

################# typical activities #####################################
act_cinema  = Activity_theoric([(100,10)], "cinema", (9,22),1.5)
act_balade  = Activity_theoric([(100,10)], "balade", (9,19),1)
act_sport  = Activity_theoric([(100,10)], "sport", (9,19),1)
act_grosseries = Activity_theoric([(100,10)], "grosseries", (9,19),.5)

act_student = [act_cinema, act_balade, act_sport]
act_white_collar = [act_cinema, act_grosseries, act_sport]


##################### generating personns ##########################################

def generate_student():
	age = int(10 + random.random()*10)
	home_loc = random_home_location()
	work_loc = random_in_area(home_loc, 1000)
	person_student = Personn(age, home_loc, work_loc , work_student, act_student)
	person_student.add_job()
	person_student.add_activities()
	person_student.compute_deplacement()
	return(person_student)


def generate_white_collar():
	age = int(20 + random.random()*40)
	home_loc = random_home_location()
	work_loc = random_work_location()
	person_wc = Personn(age, home_loc, work_loc , work_white_collar, act_white_collar)
	person_wc.add_job()
	person_wc.add_activities()
	person_wc.compute_deplacement()
	return(person_wc)


######################## lets do tests #######################



nb_test = 4500
for i in range(nb_test):
	if 100*i%(nb_test)==0:
		print(100*i/(nb_test))
	person_student = generate_student()
	person_wc = generate_white_collar()



for d in person_student.travels:
	d.print_d()


for d in person_wc.travels:
	d.print_d()
