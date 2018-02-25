from config import *
# we import all the global variable of the project

import generate_transportation as gt
import generate_personns as gp

if __name__ == '__main__':
	
	network, stations, shortest_path_stations, hubs = gt.generate_transportation()
	# shortest_path_stations is a generator that contains all shortest paths
	print(len(stations))
	print(type(shortest_path_stations))

	l_p = gp.generate_personns(shortest_path_stations)
	for person in l_p:
		person.display()
		print('')


