import generate_transportation_schedule as sch
import generate_station_names as nm
import generate_transportation_geometry as geo
import transportation_display as dis
import generate_transportation_xml as xml
import generate_personns as gp

if __name__ == "__main__":
    n_lines = geo.gaussian_trunc(5, 17, 10, 3)
    print (n_lines, "lines will be generated")
    lines = geo.generate_lines(n_lines, 5000, 1000)

    #dis.display_segments(lines=lines, intersections=[], title='simple segments')

    intersections = geo.find_intersections(lines)
    #dis.display_segments(lines, intersections, 'simple segments with intersections')

    outliers, clusters = geo.points_to_glue(intersections, 600)
    glued_inter = geo.glue_inter(outliers, clusters, intersections)
    #dis.display_segments(lines, glued_inter, 'simple segments with "glued" intersections')

    merged_lines = geo.merge_lines(lines, glued_inter)
    #dis.display_network(merged_lines, glued_inter, [],[], [], 'lines crossing the intersections')

    stations = geo.generate_stations(merged_lines, 200)
    stations = geo.merge_stations(stations, glued_inter)
    #dis.display_network(merged_lines, glued_inter, stations, [], [],  'lines with stations')

    outliers, clusters = geo.points_to_glue(stations, 300)
    glued_stations = geo.glue_stations(outliers, clusters, stations)
    #dis.display_network(merged_lines, [], glued_stations, [], [],  'lines with "glued" stations')
    filtered_stations = geo.remove_duplicate_lines(glued_stations)
    
    hubs = geo.compute_hubs(filtered_stations)
    #dis.display_network(merged_lines, [], glued_stations, hubs, [], 'lines with "glued" stations and hubs')

    fast_lines = geo.build_fast_lines(hubs, 5000, 1000)
    n_fast_lines = len(fast_lines)
    print(n_fast_lines, "fast lines have been generated")


    #dis.display_network([], [], [], hubs, fast_lines, 'fast lines')

    updated_stations = geo.update_compatibilities(filtered_stations, fast_lines)
    names = nm.generate_names(len(updated_stations))
    updated_stations = nm.add_names(names, updated_stations)
    lines_dict = sch.build_lines_dict(updated_stations)
    lines_dict = sch.remove_gaps_in_ordering(lines_dict)
    lines_dict = sch.compute_whole_schedule(lines_dict, 'friday')

    xml.generate_xml(lines_dict)
    
