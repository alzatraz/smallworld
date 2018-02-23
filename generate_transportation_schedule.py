import networkx as nx
import numpy as np
import generate_transportation_geometry as geo
from collections import defaultdict

####################
# Helper functions #
####################

def add_times(time, delta):
    delta_hour, delta_minute, delta_second = delta
    hour, minute, second = time
    total_seconds = convert_to_seconds(time) + convert_to_seconds(delta)
    return rectify(convert_to_tuple(total_seconds))


def convert_to_tuple(seconds):
    n_hours = int(seconds/3600)
    seconds = seconds-n_hours*3600
    n_minutes = int(seconds/60)
    n_seconds = seconds - n_minutes*60
    return (n_hours, n_minutes, n_seconds)


def convert_to_seconds(time_tuple):
    hour, minute, second = time_tuple
    return hour*3600+minute*60+second


def tuple_minus(time_tuple):
    return (-time_tuple[0], -time_tuple[1], -time_tuple[2])


def rectify(time_tuple):
    hour, minute, second = time_tuple
    if second < 0 and minute < 0:
        hour = 23
        second = 60+second
        minute = 60+minute-1
    if hour > 23:
        hour -= 24
    return(hour, minute, second)


def is_less_or_equal(time_tuple1, time_tuple2):
    # time between 5 and 1
    hour1, minute1, second1 = time_tuple1
    hour2, minute2, second2 = time_tuple2
    if hour1 == 0 or hour1 == 1:
        hour1 += 24
    if hour2 == 0 or hour2 == 1:
        hour2 += 24
    time1 = convert_to_seconds((hour1, minute1, second1))
    time2 = convert_to_seconds((hour2, minute2, second2))
    return time1 <= time2


##################
# Data synthesis #
##################


class Network(object):
    def __init__(self, lines=[]):
        self.lines = lines

    def add_line(self, line):
        self.lines.append(line)

    def get_line_by_name(self, line_name):
        lines = self.lines
        for line in lines:
            if line.name == line_name:
                return line
    def display(self):
        print('The Network contains ' + str(len(self.lines)) + ' lines')
        for line in self.lines:
            line.display()
            print('\n')

    def get_n_lines(self):
        return len(self.lines)

    def get_all_stations(self):
        stations = []
        for line in self.lines:
            for station in line.stations:
                if station not in stations:
                    stations.append(station)
        return stations

    def display_schedule(self, line_name, station_number, day_type, direction):
        line = self.get_line_by_name(line_name)
        if day_type == 'wd':
            if direction == 'f':
                print(line.schedule.wd_forward[station_number-1])
            else:
                print(line.schedule.wd_backward[station_number-1])
        else:
            if direction == 'f':
                print(line.schedule.we_forward[station_number-1])
            else:
                print(line.schedule.we_backward[station_number-1])



                



class Line(object):
    def __init__(self, name=None, speed=None, stations=[], schedule=None):
        self.stations = stations
        self.name = name
        self.speed = speed
        self.schedule = schedule

    def display(self):
        print('Line ' + str(self.name))
        print('Speed ' + str(self.speed) + ' m/s')
        print('Contains ' + str(len(self.stations)) + ' stations :')
        for station in self.stations:
            print(station.name)

    def get_n_stations(self):
        return(len(self.stations))

    def get_station_by_name(self, station_name):
        for station in self.stations:
            if station.name == name:
                return station


def build_lines_dict(stations):
    lines_dict = defaultdict(list)
    for station in stations:
        lines_and_numbers = station.compats
        for line, _ in lines_and_numbers:
            lines_dict[line].append(station)
    return lines_dict

def build_Network(lines_dict, slow_speed, fast_speed):
    network = Network()
    for (j, (line_name, stations)) in enumerate(lines_dict.items()):
        #network.lines.append(Line(line_name))
        station_to_number = []
        new_stations = []
        for station in stations:
            station_to_number.append((station, station.query_number(line_name)))
        station_to_number = sorted(station_to_number, key=lambda x: x[1])
        for (i, (station, number)) in enumerate(station_to_number):
            new_station = station.set_number((line_name, number), i+1)
            new_stations.append(new_station)
        if type(line_name) == int:
            speed = slow_speed
        else:
            speed = fast_speed
        line = Line(line_name, speed, new_stations)
        network.add_line(line)
    return network


#######################
# Schedule generation #
#######################

def start_end_terminus(day):
    if day == 'saturday' or day == 'friday':
        offset = 1
    else:
        offset = 0
    start_minutes = np.random.uniform(30, 59, 2)
    end_minutes = np.random.uniform(0, 59, 2)
    end_seconds = np.random.uniform(0, 59, 2)
    start_seconds = np.random.uniform(0, 59, 2)
    start_times, end_times = [], []
    for i in range(0, 2):
        minute = int(end_minutes[i])
        second = int(end_seconds[i])
        if minute in range(0, 30):
            end_times.append((0+offset, minute, second))
        else:
            end_times.append((0+offset, minute, second))
        minute = int(start_minutes[i])
        second = int(start_seconds[i])
        start_times.append((5, minute, second))
    return start_times, end_times


def compute_times_between_stations(line_name, line, speed):
    times_between = []
    n_stations = line.get_n_stations()
    point_to_number = {}

    l = []
    for i, station in enumerate(line.stations):
        l.append(station.coords)
        point_to_number[station.coords] = station.query_number(line_name)
    # problème au niveau du dictionnaire !!!
    # la ligne contient plusieurs points identiques !!
    # il faut regarder la fonction 
    points = sorted(point_to_number, key=point_to_number.get)

    for i in range(0, n_stations-1):
        p1 = points[i]
        p2 = points[i+1]
        dist = p1.distance(p2)
        time_between = int(dist/speed)
        times_between.append(time_between)
    return times_between


def generate_departure_times(start):
    if is_less_or_equal(start, (7, 30, 0)):
        mu = 6*60
        sigma = 3*60
    else:
        if is_less_or_equal(start, (10, 0, 0)):
            mu = 2*60
            sigma = 30
        else:
            if is_less_or_equal(start, (18, 0, 0)):
                mu = 4*60
                sigma = 2*60
            else:
                if is_less_or_equal(start, (21, 0, 0)):
                    mu = 2*60
                    sigma = 60
                else:
                    mu = 6*60
                    sigma = 4*60
    delta = geo.gaussian_trunc(60, 600, mu, sigma)
    delta = convert_to_tuple(delta)
    new_start = add_times(delta, start)
    return new_start


def new_time_from_previous(time_between, start):
    sigma = int(time_between/10)
    mu = 0
    mini = int(-time_between/5)
    maxi = int(time_between/2)
    delta = geo.gaussian_trunc(mini, maxi, mu, sigma)
    t = delta + time_between
    t = convert_to_tuple(t)
    new_time = add_times(start, t)
    return new_time


def compute_line_schedule(times_between, day):
    n_stations = len(times_between) + 1

    schedule_forward = []
    schedule_backward = []

    start_times, end_times = start_end_terminus(day)
    [start_forward, start_backward] = start_times
    [end_forward, end_backward] = end_times

    schedule_forward = [[] for _ in range(0, n_stations)]
    schedule_backward = [[] for _ in range(0, n_stations)]

    schedule_forward[0].append(start_forward)
    schedule_backward[-1].append(start_backward)

    time_forward, time_backward = start_forward, start_backward

    for i in range(1, n_stations):
        time_between = times_between[i-1]
        time_forward = new_time_from_previous(time_between, time_forward)
        schedule_forward[i].append(time_forward)

        time_between = times_between[n_stations-i-1]
        time_backward = new_time_from_previous(time_between, time_backward)
        schedule_backward[n_stations-i-1].append(time_forward)

    forward_end, backward_end = False, False


    while True:
        start_forward = generate_departure_times(start_forward)
        start_backward = generate_departure_times(start_backward)

        if not is_less_or_equal(start_forward, end_backward):
            forward_end = True
        if not is_less_or_equal(start_backward, end_forward):
            backward_end = True

        if forward_end and backward_end:
            break
        schedule_forward[0].append(start_forward)
        schedule_backward[0].append(start_backward)

        time_forward = start_forward
        time_backward = start_backward

        for i in range(1, n_stations):
            if not forward_end:
                time_between = times_between[i-1]
                time_forward = new_time_from_previous(time_between,
                                                      time_forward)
                schedule_forward[i].append(time_forward)
            if not backward_end:
                time_between = times_between[n_stations-i-1]
                time_backward = new_time_from_previous(time_between,
                                                       time_backward)
                schedule_backward[i].append(time_backward)
    return schedule_forward, schedule_backward

class Schedule(object):
    def __init__(self, wd_forward=None, wd_backward=None, we_forward=None, we_backward=None):
        self.wd_forward = wd_forward
        self.wd_backward = wd_backward
        self.we_forward = we_forward
        self.we_backward = we_backward

def compute_whole_schedule2(lines_dict):
    for line_id in lines_dict.keys():
        line = lines_dict[line_id]
        if type(line_id) == int:
            speed = 'slow'
        else:
            speed = 'fast'
        times_between = compute_times_between_stations(line_id, line, speed)
        schedule_we = compute_line_schedule(times_between, 'Saturday')
        schedule_wd = compute_line_schedule(times_between, 'Monday')
        we_forward, we_backward = schedule_we
        wd_forward, wd_backward = schedule_wd
        for i, station in enumerate(line):
            number = station.query_number(line_id)
            station_schedule = Schedule(wd_forward[number], wd_backward[number], we_forward[number], we_backward[number])
            lines_dict[line_id][i].schedule = station_schedule
    return lines_dict

def compute_whole_schedule(network):
    for line in network.lines:
        speed = line.speed
        line_name = line.name
        times_between = compute_times_between_stations(line_name, line, speed)
        schedule_we = compute_line_schedule(times_between, 'saturday')
        schedule_wd = compute_line_schedule(times_between, 'monday')
        we_forward, we_backward = schedule_we
        wd_forward, wd_backward = schedule_wd
        line.schedule = Schedule(wd_forward, wd_backward, we_forward, we_backward)
    return network



#################################
# Graph definition and Dijkstra #
#################################


def convert_Network_to_Graph(network):
    graph = nx.Graph()
    stations = network.get_all_stations()
    for station in stations:
        graph.add_node(station)
    for line in network.lines:
        stations = line.stations
        n_stations = line.get_n_stations()
        for i in range(1, n_stations):
            graph.add_edge(stations[i-1], stations[i])
    return graph

def shortest_path(graph, departure, arrival):
    return nx.shortest_path(graph, departure, arrival)



