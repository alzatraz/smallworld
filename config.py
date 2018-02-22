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

r_line_mu = 5000  # average distance between a line terminal and the center
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

close_stations_sensitivity = 300  # number of meters below which two
                                  # intersections will form a cluster and will
                                  # be glued together

##############################
# To generate the fast lines #
##############################

min_n_stations_per_fast_line = 3  # minimal number of stations to keep a fast
                                  # line that has been generated

n_meters = 500  # coefficient (in meters) that determines the attractivity of
				# a hub when multiplied with its ranking (number of lines that
				# cross it). Te attractivity is the radius below which a line
				# crossing the area within this radius will bend to cross the
				# hub)

