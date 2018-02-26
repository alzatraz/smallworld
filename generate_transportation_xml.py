from rdflib import *
from xml.etree.ElementTree import Element, SubElement, ElementTree


def complete_with_zero(i):
    if i in range(0, 10):
        return ('0' + str(i))
    return str(i)

def time_tuple_to_string(time_tuple):
    string_time = ""
    for time in time_tuple:
        string_time = string_time + complete_with_zero(time) + ":"
    return string_time[:-1]


def generate_rdf(network):
    g = Graph()
    schema = Namespace('http://schema.org/')
    smallworld = 'http://smallworld.org/'
    for line in network.lines:
        name = line.name
        if type(name) == int:
            line_name = 'Métro Ligne ' + str(name)
            line_path = 'M' + str(name)
        else:
            line_name = 'RER Ligne ' + name
            line_path = 'RER' + name
        line_path = smallworld + 'lines/' + line_path + '/'
        line_uri = URIRef(line_path)
        g.add((line_uri, schema.name, Literal(line_name)))
        schedule = line.schedule
        wd_f, wd_b, we_f, we_b = schedule.wd_forward, schedule.wd_backward, schedule.we_forward, schedule.we_backward
        for j, station in enumerate(line.stations):
            wd_f_station, wd_b_station, we_f_station, we_b_station = wd_f[j], wd_b[j], we_f[j], we_b[j]
            point = station.coords
            station_name = station.name
            coords = BNode()
            g.add((coords, schema.latitude, Literal(point[0])))
            g.add((coords, schema.longitude, Literal(point[1])))
            station_uri = URIRef(smallworld + 'stations/' + str(name) + '/')
            g.add((station_uri, schema.geo, coords))
            g.add((line_uri, schema.containsPlace, station_uri))
            g.add((station_uri, schema.name, Literal(station_name)))
            dep_wd_f, dep_wd_b, dep_we_f, dep_we_b = BNode(), BNode(), BNode(), BNode()
            g.add((line_uri, schema.event, dep_wd_f))
            g.add((line_uri, schema.event, dep_wd_b))
            g.add((line_uri, schema.event, dep_we_f))
            g.add((line_uri, schema.event, dep_we_b))
            for time_tuple in wd_f_station:
                dep_wd_f_one = BNode()
                g.add((dep_wd_f_one, schema.subEvent, dep_wd_f))
                time = time_tuple_to_string(time_tuple)
                g.add((dep_wd_f_one, schema.startDate, Literal(time)))
            for time_tuple in wd_b_station:
                dep_wd_b_one = BNode()
                g.add((dep_wd_b_one, schema.subEvent, dep_wd_b))
                time = time_tuple_to_string(time_tuple)
                g.add((dep_wd_b_one, schema.startDate, Literal(time)))
            for time_tuple in we_f_station:
                dep_we_f_one = BNode()
                g.add((dep_we_f_one, schema.subEvent, dep_we_f))
                time = time_tuple_to_string(time_tuple)
                g.add((dep_we_f_one, schema.startDate, Literal(time)))
            for time_tuple in we_b_station:
                dep_we_b_one = BNode()
                g.add((dep_wd_b_one, schema.subEvent, dep_we_b))
                time = time_tuple_to_string(time_tuple)
                g.add((dep_wd_b_one, schema.startDate, Literal(time)))
    g.serialize("xml_outputs/transportation.rdf")
    return g

def write_schedule(line, schedule):
    schedule_xml = SubElement(line, 'line_schedule')
    wd_forward = schedule.wd_forward
    wd_backward = schedule.wd_backward
    we_forward = schedule.we_forward
    we_backward = schedule.we_backward
    schedules_names = ['wd_forward', 'wd_backward', 'we_forward', 'we_backward']
    schedules = [wd_forward, wd_backward, we_forward, we_backward]
    for sch_name, sch_values in zip(schedules_names, schedules):
        attrs = {'direction' : sch_name[-7:], 'day' : sch_name[:2]}
        sch_xml = SubElement(schedule_xml, 'sub_schedule', attrs)
        for station_schedule in sch_values:
            sch_station_xml = SubElement(sch_xml, 'station_schedule')
            for time_tuple in station_schedule:
                time = time_tuple_to_string(time_tuple)
                time_xml = SubElement(sch_station_xml, 'time')
                time_xml.text = time


def generate_xml(network):
    network_xml = Element('network')
    for line in network.lines:
        attrs_names = ['name', 'speed']
        attrs_values = [str(line.name), str(line.speed)]
        attrs = dict(zip(attrs_names, attrs_values))
        line_xml = SubElement(network_xml, 'line', attrs)
        stations = line.stations
        whole_schedule = line.schedule
        wd_forward = whole_schedule.wd_forward
        wd_backward = whole_schedule.wd_backward
        we_forward = whole_schedule.we_forward
        we_backward = whole_schedule.we_backward
        for i, station in enumerate(stations):
            station_name = station.name
            station_x, station_y = station.coords[0], station.coords[1]
            station_compats = station.compats
            station_xml = SubElement(line_xml, 'station', {'name' : station_name})
            station_coords_xml = SubElement(station_xml, 'coordinates', {'x' : str(station_x), 'y' : str(station_y)})
            station_compats_xml = SubElement(station_xml, 'compatibilities')
            for station_compat in station_compats:
                line = str(station_compat[0])
                number = str(station_compat[1])
                station_compat_xml = SubElement(station_compats_xml, 'compatibility', {'line' : line, 'station' : number})
            schedules = [wd_forward[i], wd_backward[i], we_forward[i], we_backward[i]]
            schedules_names = ['wd_forward', 'wd_backward', 'we_forward', 'we_backward']
            for schedule, schedule_name in zip(schedules, schedules_names):

                attrs = {'direction' : schedule_name[3:], 'day' : schedule_name[:2]}
                schedule_xml = SubElement(station_xml, 'schedule', attrs)
                for time_tuple in schedule:
                    time = time_tuple_to_string(time_tuple)
                    time_xml = SubElement(schedule_xml, 'time')
                    time_xml.text = time
    ElementTree(network_xml).write('xml_outputs/transportation.xml') 

if __name__ == "__main__":
    """lines_dict = {0 : [[(0, 0), 5, 'Châtelet', [(2, 30, 1), (3, 14, 20), (10, 15, 4), (11, 15, 41)], [(1, 5, 4), (1, 2, 74), (15, 4, 8), (4, 15, 4)]], [(0, 1), 4, 'Pont-Neuf', [(7,4, 8), (7, 9, 54)], [(4, 74, 5), (4, 54, 21)]]]}
                g = generate_rdf(lines_dict)
                print(g.serialize())
                g.serialize("test.rdf")"""

