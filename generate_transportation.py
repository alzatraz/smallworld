import generate_transportation_schedule as sch
import generate_station_names as nm
import generate_transportation_geometry as geo
import transportation_display as dis
import generate_transportation_xml as xml
import generate_personns as gp
from config import *
import generate_itinerary as it

def generate_hubs():
    

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

    outliers, clusters = geo.points_to_glue(stations,
                                            close_stations_sensitivity)
    glued_stations = geo.glue_stations(outliers, clusters, stations)
    filtered_stations = geo.remove_duplicate_lines(glued_stations)
    hubs = geo.compute_hubs(filtered_stations)
    return hubs, filtered_stations

def generate_transportation():
    # Global topology : lines
    n_lines = geo.gaussian_trunc(n_lines_mini, n_lines_maxi, n_lines_mu,
                                 n_lines_sigma)
    lines = geo.generate_lines(n_lines, r_line_mu, r_line_sigma)
    intersections = geo.find_intersections(lines)
    outliers, clusters = geo.points_to_glue(intersections,
                                            intersection_sensitivity)
    glued_inter = geo.glue_inter(outliers, clusters, intersections)
    merged_lines = geo.merge_lines(lines, glued_inter)

    # Local topology : stations
    stations = geo.generate_stations(merged_lines, position_variance,
                                     av_dist_btw_stations)
    stations = geo.merge_stations(stations, glued_inter)
    outliers, clusters = geo.points_to_glue(stations,
                                            close_stations_sensitivity)
    glued_stations = geo.glue_stations(outliers, clusters, stations)
    filtered_stations = geo.remove_duplicate_lines(glued_stations)
    hubs = geo.compute_hubs(filtered_stations)
    fast_lines = geo.build_fast_lines(hubs, r_line_mu, r_line_sigma,
                                      min_n_stations_per_fast_line, n_meters)
    n_fast_lines = len(fast_lines)
    updated_stations = geo.update_compatibilities(filtered_stations,
                                                  fast_lines)

    # Toponymy
    names = nm.generate_names(len(updated_stations))
    updated_stations = nm.add_names(names, updated_stations)
    lines_dict = sch.build_lines_dict(updated_stations)
    network = sch.build_Network(lines_dict, slow_speed, fast_speed)

    # Schedule and itineraries
    network = sch.compute_whole_schedule(network)
    stations = network.get_all_stations()
    graph = it.convert_Network_to_Graph(network)
    all_shortest_paths = it.all_shortest_paths_and_lengths(graph)
    xml.generate_xml(network)
    xml.generate_rdf(network)
    return network, stations, all_shortest_paths, hubs

if __name__ == "__main__":    
    

    # Global topology : lines
    n_lines = geo.gaussian_trunc(n_lines_mini, n_lines_maxi, n_lines_mu,
                                 n_lines_sigma)
    lines = geo.generate_lines(n_lines, r_line_mu, r_line_sigma)
    dis.display_segments(lines, [], 'simple segments')
    intersections = geo.find_intersections(lines)
    dis.display_segments(lines, intersections,
                         'simple segments with intersections')
    outliers, clusters = geo.points_to_glue(intersections,
                                            intersection_sensitivity)
    glued_inter = geo.glue_inter(outliers, clusters, intersections)
    dis.display_segments(lines, glued_inter,
                         'simple segments with "glued" intersections')
    merged_lines = geo.merge_lines(lines, glued_inter)
    dis.display_network(merged_lines, glued_inter, [],[], [],
                        'lines crossing the intersections')

    # Local topology : stations
    stations = geo.generate_stations(merged_lines, position_variance,
                                     av_dist_btw_stations)
    stations = geo.merge_stations(stations, glued_inter)
    dis.display_network(merged_lines, glued_inter, stations, [], [],
                        'lines with stations')
    outliers, clusters = geo.points_to_glue(stations,
                                            close_stations_sensitivity)
    glued_stations = geo.glue_stations(outliers, clusters, stations)
    dis.display_network(merged_lines, [], glued_stations, [], [],
                        'lines with "glued" stations')
    filtered_stations = geo.remove_duplicate_lines(glued_stations)
    hubs = geo.compute_hubs(filtered_stations)
    dis.display_network(merged_lines, [], glued_stations, hubs, [],
                        'lines with "glued" stations and hubs')
    fast_lines = geo.build_fast_lines(hubs, r_line_mu, r_line_sigma,
                                      min_n_stations_per_fast_line, n_meters)
    n_fast_lines = len(fast_lines)
    dis.display_network([], [], [], hubs, fast_lines, 'fast lines')
    updated_stations = geo.update_compatibilities(filtered_stations,
                                                  fast_lines)

    # Toponymy
    names = nm.generate_names(len(updated_stations))
    updated_stations = nm.add_names(names, updated_stations)
    lines_dict = sch.build_lines_dict(updated_stations)
    network = sch.build_Network(lines_dict, slow_speed, fast_speed)

    # Schedule and itineraries
    network = sch.compute_whole_schedule(network)
    stations = network.get_all_stations()
    from sympy.geometry import Point
    graph = it.convert_Network_to_Graph(network)
    p1 = Point(5000, 5000)
    p2 = Point(-5000, -5000)
    path = it.shortest_path(graph, p1, p2)
    dis.display_path_on_network(p1, p2, path, network, 'path on a network')
    xml.generate_xml(network)
