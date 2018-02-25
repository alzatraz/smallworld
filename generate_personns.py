import numpy as np 
import random 
import math
import pylab as pl
from matplotlib import collections  as mc
from matplotlib.patches import Circle, Wedge, Polygon
import time
import xml.etree as etree
from xml.etree import ElementTree
import xml.etree.cElementTree as ET
import xml.dom.minidom
 


############ global variables ###############

########## dont touch###########
pi = 3.14159265359 
color_work = (1, 0, 0, 1)
color_activity = (0, 1, 0, 1)
color_home = (0, 0, 1, 1)


stations = []
shortest_path_stations = {}
closest_station = {}


########## play with that###########
nb_of_days = 7
p_outing_work = .8
p_outing_not_work = .8
size_pop = 10

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

p_solo = .1
p_nb_child = [.2,.5, .75, .85, .95, 1]

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

def closest_station_of(pos):
	if pos in closest_station.keys():
		return(closest_station[pos])
	else:
		s = choose_place(stations, pos)
		closest_station[pos] =s
		return(s)


class Deplacement:
	def __init__(self):
		self.start = (0,0)
		self.end = (0,0)
		self.day = 0
		self.hour = 0
		self.tag = "none"
		self.stations_list =[]

	def __init__(self, start, end, day, hour ):
		self.start = start
		self.end = end
		self.day = day
		self.hour = hour
		self.tag = "none"
		self.stations_list =[]

	def __init__(self, start, end, day, hour ,tag):
		self.start = start
		self.end = end
		self.day = day
		self.hour = hour
		self.tag = tag
		self.stations_list =[]

	def compute_station_list(self):
		start_station = closest__station_of(self.start)
		end_station = closest__station_of(self.end)
		self.stations_list = shortest_path_stations[(start_station, end_station)]


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

def give_id():
	return(int(random.random()*1000000))

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
		self.id = give_id()
		self.family = []

	def __init__(self, age,home,work_place,work,activities):
		self.name = "pablo"
		self.id = give_id()		
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
					self.planning[d].append( (a_real.place, a_real.shedule[0], a_real.shedule[1], "activity" )  )

			else:
				if(r<p_outing_not_work):
					a = self.random_activity()
					a_real = Activity_real(a,self,d)
					self.planning[d].append( (a_real.place, a_real.shedule[0], a_real.shedule[1] , "activity" )  )				

	def compute_deplacement(self):
		for day in range(nb_of_days):
			to_do = self.planning[day]
			act_loc = self.home
			for (loc , start, end,tag) in to_do:
				d1 = Deplacement(act_loc , loc ,day, start,tag)
				act_loc = loc
				self.travels.append(d1)
			if(act_loc!=self.home):
				d1 = Deplacement(act_loc , self.home ,day, end,"home")
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

def random_location_one(nb_to_put):
	l_loc = []
	w = int(math.sqrt(nb_to_put))
	for x in range(w):
		for y in range(w):
			l_loc.append((2*x*max_r/w-max_r+random.random()*1000,2*y*max_r/w-max_r+random.random()*1000))
	return(l_loc)


def random_location_grosseries():
	nb_to_put = max_r*max_r*pi/1000000*density_grosseries_outer
	return(random_location_one(nb_to_put))

def random_location_sport():
	nb_to_put = 36
	return(random_location_one(nb_to_put))

def random_location_cinema():
	nb_to_put = 49
	return(random_location_one(nb_to_put))


 ################# generating typical types ###############################
################# typical working type #######################################
work_no_work = Work("no work", (0,0) ,[False, False, False, False	, False, False, False ] )
work_white_collar = Work("white collar", (9,19) ,[True, True, True, True, True, False, False ] )
work_student = Work("school", (8,17) ,[True, True, False, True, True, False, False ] )

################# typical activities #####################################
act_cinema  = Activity_theoric(random_location_cinema(), "cinema", (9,22),1.5)
act_sport  = Activity_theoric(random_location_sport(), "sport", (9,19),1)
act_grosseries = Activity_theoric(random_location_grosseries(), "grosseries", (9,19),.5)

act_student = [act_cinema, act_sport]
act_white_collar = [act_cinema, act_grosseries, act_sport]


##################### generating personns ##########################################

def generate_student(home_loc ):
	age = int(10 + random.random()*10)
	work_loc = random_in_area(home_loc, 1000)
	person_student = Personn(age, home_loc, work_loc , work_student, act_student)
	person_student.add_job()
	person_student.add_activities()
	person_student.compute_deplacement()
	return(person_student)


def generate_white_collar(home_loc ):
	age = int(20 + random.random()*40)
	work_loc = random_work_location()
	person_wc = Personn(age, home_loc, work_loc , work_white_collar, act_white_collar)
	person_wc.add_job()
	person_wc.add_activities()
	person_wc.compute_deplacement()
	return(person_wc)

def add_marital_personn(fam):
	n_fam = fam
	sec_wc = generate_white_collar(fam[0].home)
	for p in fam:
		p.family.append(sec_wc)
		sec_wc.family.append(p)
	fam.append(sec_wc)
	return(n_fam)

def add_child(fam):
	n_fam = fam
	sec_wc = generate_student(fam[0].home)
	for p in fam:
		p.family.append(sec_wc)
		sec_wc.family.append(p)
	fam.append(sec_wc)
	return(n_fam)

def generate_family():
	family =[]
	one_wc = generate_white_collar(random_home_location())
	family.append(one_wc)
	
	r = random.random()
	if r<p_solo:
		return(family)
	family = add_marital_personn(family)
	
	r = random.random()
	i=0
	while(r>p_nb_child[i]):
		i+=1
		family = add_child(family)
	return(family)

##################### displaying travels####################

def clean_travel(d):
	col = color_home
	if d.tag=="activity":
		col = color_activity
	if d.tag=="work":
		col = color_work
	return([d.start, d.end],col)

def display_activities(cinemas, grosseries, sports):
	l_x = []
	l_y = []
	for (x,y) in cinemas:
		l_x.append(x)
		l_y.append(y)
	pl.plot(l_x, l_y, 'ko',ms = 1.5)
	l_x = []
	l_y = []
	for (x,y) in grosseries:
		l_x.append(x)
		l_y.append(y)
	pl.plot(l_x, l_y, 'yo',ms = 1.5)
	l_x = []
	l_y = []
	for (x,y) in sports:
		l_x.append(x)
		l_y.append(y)
	pl.plot(l_x, l_y, 'mo', ms = 1.5)




def display_travels(list_p, day):
	to_disp =[]
	colors =[]
	for p in list_p:
		l_t = p.travels
		for t in l_t:
			to_print = clean_travel(t)
			to_disp.append(to_print[0])
			colors.append(to_print[1])
	lc = mc.LineCollection(to_disp,colors=colors,linewidths=1)
	fig, ax = pl.subplots()
	ax.add_collection(lc)
	ax.autoscale()
	ax.margins(0.1)
	circle1 = Circle((0, 0), r_center_paris,color = 'r', alpha = .1)
	circle2 = Circle((0, 0), max_r,color = 'blue', alpha = .1)
	ax.add_artist(circle1)
	ax.add_artist(circle2)

##########################  CREATION OF the xml file ##########

def xml_travel(t, father):
	travel = ET.SubElement(father, "travel", name = t.tag)
	start  = ET.SubElement(travel, "start")
	ET.SubElement(start, "x", value = str(t.start[0]))
	ET.SubElement(start, "y", value = str(t.start[1]))
	end  = ET.SubElement(travel, "end")
	ET.SubElement(end, "x", value = str(t.end[0]))
	ET.SubElement(end, "y", value = str(t.end[1]))
	day = ET.SubElement(travel, "day", value = str(t.day))
	hour = ET.SubElement(travel, "hour", value = str(t.hour))
	
def xml_family(p, father):
	if len(p.family)>0:
		ET.SubElement(father, "wife", value = str(p.family[0].id))
		for i in range(len(p.family)-1):
			ET.SubElement(father, "child", value = str(p.family[i+1].id))


def xml_personn(p,father):
	pers_n = ET.SubElement(father, "person", value=str(p.id))
	home_n = ET.SubElement(pers_n,"home")
	ET.SubElement(home_n,"x", value = str(p.home[0]))
	ET.SubElement(home_n,"y", value = str(p.home[1]))
	ET.SubElement(pers_n,"name").text = (p.name)
	ET.SubElement(pers_n,"age", value = str(p.age))
	family = ET.SubElement(pers_n,"family", value = str(len(p.family)))
	xml_family(p,family)
	work_n = ET.SubElement(pers_n,"work")
	work_loc_n = ET.SubElement(work_n,"work_location")
	ET.SubElement(work_loc_n,"x", value = str(p.work_place[0]))
	ET.SubElement(work_loc_n,"y", value = str(p.work_place[1]))	
	ET.SubElement(work_n,"work_shedule", name="shedule" )
	travels = ET.SubElement(pers_n,"travels")
	for t in p.travels:
		xml_travel(t , travels)




def xml_total(l_p):
	root = ET.Element("root")
	doc = ET.SubElement(root, "doc")
	for p in l_p:
		xml_personn(p, doc)
	tree = ET.ElementTree(root)
	tree.write("persons.xml")


######################## lets do tests #######################


if __name__ == "__main__":
	start_time = time.time()
	l_p = []
	for i in range(size_pop):
		if 100*i%(size_pop)==0:
			print(100*i/(size_pop))
		fam = generate_family()
		for p in fam:
			l_p.append(p)
	print("generating  persons --- %s seconds ---" % (time.time() - start_time))


"""	start_time = time.time()
	xml_total(l_p)
	print("generating xml --- %s seconds ---" % (time.time() - start_time))	
	display_travels(l_p, 0)
	display_activities(act_cinema.possible_places,act_grosseries.possible_places,act_sport.possible_places)
	pl.show()

	print("\n student ")

	for d in person_student.travels:
		d.print_d()

	print("\n white collar travels : ")

	for d in person_wc.travels:
		d.print_d()
"""