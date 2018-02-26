
#########################################
# Color settings for trip visualization #
#########################################

pi = 3.14159265359 
color_work = (1, 0, 0, 1)
color_activity = (0, 1, 0, 1)
color_home = (0, 0, 1, 1)

######################
# Trip probabilities #
######################

p_outing_work = .5
p_outing_not_work = .8
p_live_center = .07
p_work_center = .8

#########################
# Geographic parameters #
#########################

r_center_paris = 3000
max_r = 7000
density_cinema_center = 97/105.1
density_cinema_outer = .2

density_sport_center = .5
density_sport_outer = .5

density_grosseries_center = .5
density_grosseries_outer = .5

#####################
# Family parameters #
#####################

p_not_celib = 1
p_nb_child = [.2,.5, .75, .85, .95, 1]
size_pop = 3


###################
# Simulation time #
###################
nb_of_days = 7



##########################################
# To generate the number of 'slow' lines #
##########################################

n_lines_mini = 5  # minimum number of lines
n_lines_maxi = 17  # maximum number of lines
n_lines_mu = 10  # average number of lines
n_lines_sigma = 3  # standard deviation for the number of lines


##########################################
# To generate the terminals of the lines #
##########################################

r_line_mu = max_r  # average distance between a line terminal and the center
r_line_sigma = 1000  # average standard deviation for the distance between 
				     # theline terminal and the city center


#####################################################
# To generate the glued intersections between lines #
#####################################################

intersection_sensitivity = 600  # number of meters below which two intersections
							  # will form a cluster and will be glued together

############################
# To generate the stations #
############################

av_dist_btw_stations = 710  # average distance between stations, used to
                            # generate the theoretical station locations (at
                            # regular intervals on the line)

position_variance = 200  # standard deviation for the x and y position of a
                         # station, around its theoretical location

#######################################
# To generate the aggregated stations #
#######################################

close_stations_sensitivity = 200  # number of meters below which two
                                  # intersections will form a cluster and will
                                  # be glued together

##############################
# To generate the fast lines #
##############################

min_n_stations_per_fast_line = 4  # minimal number of stations to keep a fast
                                  # line that has been generated

n_meters = 400  # coefficient (in meters) that determines the attractivity of
				# a hub when multiplied with its ranking (number of lines that
				# cross it). Te attractivity is the radius below which a line
				# crossing the area within this radius will bend to cross the
				# hub)
slow_speed = 25000/3600  # speed in meters per seconds for slow lines
fast_speed = 40000/3600  # speed in meters per seconds for fast lines

