import generate_transportation_schedule as sch
import generate_station_names as nm
import generate_transportation_geometry as geo
import transportation_display as dis
import generate_transportation_xml as xml
import generate_personns as gp
import config as cfg
import generate_itinerary as it

def generate_hubs():
    n_lines_mini = cfg.n_lines_mini
    n_lines_maxi = cfg.n_lines_maxi
    n_lines_mu = cfg.n_lines_mu
    n_lines_sigma = cfg.n_lines_sigma
    r_line_mu = cfg.r_line_mu
    r_line_sigma = cfg.r_line_sigma
    intersection_sensitivity = cfg.intersection_sensitivity
    av_dist_btw_stations = cfg.av_dist_btw_stations
    position_variance = cfg.position_variance

    n_lines = geo.gaussian_trunc(n_lines_mini, n_lines_maxi, n_lines_mu,
                                 n_lines_sigma)

    lines = geo.generate_lines(n_lines, r_line_mu, r_line_sigma)
    intersections = geo.find_intersections(lines)
    outliers, clusters = geo.points_to_glue(intersections,
                                            intersection_sensitivity)
    glued_inter = geo.glue_inter(outliers, clusters, intersections)
    merged_lines = geo.merge_lines(lines, glued_inter)
    stations = geo.generate_stations(merged_lines, position_variance,
                                     av_dist_btw_stations)
    stations = geo.merge_stations(stations, glued_inter)

    close_stations_sensitivity = cfg.close_stations_sensitivity
    outliers, clusters = geo.points_to_glue(stations,
                                            close_stations_sensitivity)
    glued_stations = geo.glue_stations(outliers, clusters, stations)
    filtered_stations = geo.remove_duplicate_lines(glued_stations)
    hubs = geo.compute_hubs(filtered_stations)
    return hubs, filtered_stations

if __name__ == "__main__":

	# Global variables import
    n_lines_mini = cfg.n_lines_mini
    n_lines_maxi = cfg.n_lines_maxi
    n_lines_mu = cfg.n_lines_mu
    n_lines_sigma = cfg.n_lines_sigma
    r_line_mu = cfg.r_line_mu
    r_line_sigma = cfg.r_line_sigma
    intersection_sensitivity = cfg.intersection_sensitivity
    min_n_stations_per_fast_line = cfg.min_n_stations_per_fast_line
    n_meters = cfg.n_meters
    av_dist_btw_stations = cfg.av_dist_btw_stations
    slow_speed = cfg.slow_speed
    fast_speed = cfg.fast_speed


    

    
    # Preprocessing
    n_lines = geo.gaussian_trunc(n_lines_mini, n_lines_maxi, n_lines_mu,
                                 n_lines_sigma)

    print (n_lines, "lines will be generated")

    lines = geo.generate_lines(n_lines, r_line_mu, r_line_sigma)
    # lines is a list of Segments

    dis.display_segments(lines=lines, intersections=[], title='simple segments')

    intersections = geo.find_intersections(lines)

    # intersections is a list, each intersection being a tuple composed of a
    # point and a list of lines that cross it

    dis.display_segments(lines, intersections, 'simple segments with intersections')


    outliers, clusters = geo.points_to_glue(intersections,
                                            intersection_sensitivity)
    # outliers is a list of Point ids that will remain unchanged
    # clusters is a dict whose values are the lists of intersections to glue

    glued_inter = geo.glue_inter(outliers, clusters, intersections)
    # glued_inter is a list of tuples composed of a Point and its compatibilities
    

    dis.display_segments(lines, glued_inter, 'simple segments with "glued" intersections')

    merged_lines = geo.merge_lines(lines, glued_inter)
    # merged_lines is a list of lists of Segments

    dis.display_network(merged_lines, glued_inter, [],[], [], 'lines crossing the intersections')



    # Stations generation
    position_variance = cfg.position_variance
    stations = geo.generate_stations(merged_lines, position_variance,
                                     av_dist_btw_stations)


    stations = geo.merge_stations(stations, glued_inter)
    dis.display_network(merged_lines, glued_inter, stations, [], [],  'lines with stations')

    close_stations_sensitivity = cfg.close_stations_sensitivity
    outliers, clusters = geo.points_to_glue(stations,
                                            close_stations_sensitivity)

    glued_stations = geo.glue_stations(outliers, clusters, stations)
    dis.display_network(merged_lines, [], glued_stations, [], [],  'lines with "glued" stations')
    filtered_stations = geo.remove_duplicate_lines(glued_stations)
    
    hubs = geo.compute_hubs(filtered_stations)
    # hubs is a list, each hub a triple composed of a Point, a rank, and a list of compatibilities

    dis.display_network(merged_lines, [], glued_stations, hubs, [], 'lines with "glued" stations and hubs')

    fast_lines = geo.build_fast_lines(hubs, r_line_mu, r_line_sigma,
                                      min_n_stations_per_fast_line, n_meters)

    n_fast_lines = len(fast_lines)
    print(n_fast_lines, "fast lines have been generated")


    dis.display_network([], [], [], hubs, fast_lines, 'fast lines')

    updated_stations = geo.update_compatibilities(filtered_stations,
                                                  fast_lines)

    # Adding names
    names = nm.generate_names(len(updated_stations))
    updated_stations = nm.add_names(names, updated_stations)

    
    lines_dict = sch.build_lines_dict(updated_stations)

    network = sch.build_Network(lines_dict, slow_speed, fast_speed)


    # Schedule computation for each day
    network = sch.compute_whole_schedule(network)

    print('number of stations', len(network.get_all_stations()))

    from sympy.geometry import Point
    graph = it.convert_Network_to_Graph(network)
    p1 = Point(3000, -1000)
    p2 = Point(-3000, 1000)
    path = it.shortest_path(graph, p1, p2)

    print(path)

    
    import matplotlib.pyplot as plt
    plt.clf()

    

    dis.display_path_on_network(p1, p2, path, network, 'path on a network')
