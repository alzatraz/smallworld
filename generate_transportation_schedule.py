import numpy as np
import generate_transportation_geometry as geo

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


def compute_times_between_stations(line, speed):
    times_between = []
    n_stations = len(line)
    if speed == 'slow':
        speed = 25000/3600
    else:
        speed = 40000/3600
    point_to_number = {}
    for i, station in enumerate(line):
        print("station0", station[0])
        point_to_number[station[0]] = station[1]
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


def compute_line_schedule(line, times_between, day):
    schedule_forward = []
    schedule_backward = []

    start_times, end_times = start_end_terminus(day)
    [start_forward, start_backward] = start_times
    [end_forward, end_backward] = end_times
    n_stations = len(line)

    schedule_forward = [[] for _ in range(0, n_stations)]
    schedule_backward = [[] for _ in range(0, n_stations)]

    schedule_forward[0].append(start_forward)
    schedule_backward[0].append(start_backward)

    for i in range(1, n_stations):
        time = new_time_from_previous(times_between, start_forward, i-1)
        schedule_forward[i].append(time)
        time = new_time_from_previous(times_between, start_backward,
                                      n_stations-i-1)
        schedule_backward[i].append(time)

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
        for i in range(1, n_stations):
            if not forward_end:
                time = new_time_from_previous(times_between,
                                              start_forward, i-1)
                schedule_forward[i].append(time)
                start_forward = time
            if not backward_end:
                time = new_time_from_previous(times_between, start_backward,
                                              n_stations-i-1)
                schedule_backward[i].append(time)
                start_backward = time
    return schedule_forward, schedule_backward


def new_time_from_previous(times_between, start, k):
    time_between = times_between[k]
    sigma = int(time_between/10)
    mu = 0
    mini = int(-time_between/5)
    maxi = int(time_between/2)
    delta = geo.gaussian_trunc(mini, maxi, mu, sigma)
    t = delta + time_between
    t = convert_to_tuple(t)
    new_time = add_times(start, t)
    return new_time


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


def compute_whole_schedule(lines_dict, day):
    for line_id in lines_dict.keys():
        line = lines_dict[line_id]
        if type(line_id) == int:
            speed = 'slow'
        else:
            speed = 'fast'
        times_between = compute_times_between_stations(line, speed)
        schedule = compute_line_schedule(line, times_between, day)
        schedule_forward, schedule_backward = schedule
        for i, station in enumerate(line):
            number = station[1]
            print("ok", lines_dict[line_id][i])
            lines_dict[line_id][i].append(schedule_forward[number])
            lines_dict[line_id][i].append(schedule_backward[number])
    return lines_dict


