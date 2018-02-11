import sympy
from sympy import *
from sympy.geometry import *
import numpy as np
import math
from scipy.stats import truncnorm
import numpy as np
from collections import defaultdict
from sklearn.cluster import DBSCAN
from sklearn import metrics
from string import ascii_uppercase

####################
# Helper functions #
####################

def gaussian_trunc(mini, maxi, mu, sigma):
    """
    Takes :
        - an int, mini (the minimum for the random variable)
        - an int, maxi (the maximum for the random variable)
        - an int, mu (the mean of the random variable)
        - an int, sigma (the standard deviation of the random variable)
    Returns :
        - an int (random number which follows a truncated gaussian distribution)
    """
    a, b = (mini-mu)/sigma, (maxi-mu)/sigma
    r = truncnorm.rvs(a, b, loc=mu, scale=sigma)
    return int(round(r))

###########################
# Generation of the lines #
###########################

def generate_lines(n_lines, mu, sigma):
    """
    Takes :
        - an int, n_lines (the number of lines to generate)
        - an int, mu (the average radius of the extremities of the line, in polar coordinates)
        - an int, sigma (the standard deviation for the radius of the extremities of the line, in polar coordinates )
    Returns :
        - a list(Segment) (the lines)
    
    Note : The function generates n_lines segments that correspond to the "skeleton" of the future
    lines. The generation uses on polar coordinates.
    First we generate the polar coordinates of the departure point, with a
    radius that will preferentially lead to the border of the city (i.e. a
    random gaussian variable centered on the "radius" of the city, e.g. 5000m),
    and a random angle (from 0 to 2*pi). Then we generate the arrival point,
    with again a random radius that will preferentially lead to the suburbs,
    and an angle that will preferentially be a 180° rotation of the first angle
    (again we use a gaussian random variable), such that the line between the
    two points is likely to come through the approximate center of the city.
    """
    lines = []
    for _ in range(0, n_lines):
        rhos = np.random.normal(mu, sigma, 2)
        theta0 = np.random.uniform(0, 2*math.pi)
        theta1 = np.random.normal(theta0-math.pi, math.pi/3)
        source = Point(int(rhos[0]*math.cos(theta0)),
                       int(rhos[0]*math.sin(theta0)))
        target = Point(int(rhos[1]*math.cos(theta1)),
                       int(rhos[1]*math.sin(theta1)))
        line = Segment(source, target)
        lines.append(line)
    return lines


def find_intersections(lines):
    """
    Finds intersections between lines.
    The output is a list of tuple, each tuple representing an intersection
    point. An intersection point is actually a pair of a Point and a list,
    containing (for th time being) 2 line ids, namely the 2 lines that
    intersect at that point.
    """
    intersections = []
    for i in range(0, len(lines)-1):
        for j in range(i+1, len(lines)):
            line1 = lines[i]
            line2 = lines[j]
            inter = intersection(line1, line2)
            if inter:
                point = inter[0]
                x, y = point[0], point[1]
                intersections.append((Point(int(x), int(y)), [i, j]))
    return intersections


def glue_inter(outliers, clusters, stations):
    centers = []
    for station_ids in clusters.values():
        # we examine the stations that will be glued together
        lines_crossing = []
        # either a list of tuples (line_id, number), or a list [line_id]
        points = []
        for station_id in station_ids:
            lines_crossing.extend(stations[station_id][1])
            points.append(stations[station_id][0])
        lines_crossing = list(set(lines_crossing))
        center = np.mean(points, axis=0)
        centers.append((Point(int(center[0]), int(center[1])), lines_crossing))
    for outlier in outliers:
        centers.append(stations[outlier])
    return (centers)


def bend_line(line, where_to_bend):
    """
    This function takes:
        - A segment (the line "skeleton")
        - A list of Points the line has to cross.
    It breaks the segment into smaller segments, whose extremities are the
    points to cross. The points to cross are "ordered" from the nearest to the
    furthest (from the source), in order to avoid zigzags. The function thus
    returns :
        - A list of Segments, which are the different linear parts of the line
    """
    bended_line = []
    source, target = line.points
    distances = {}
    for hub in where_to_bend:
        distances[source.distance(hub)] = hub
    p1 = source
    for dist in sorted(distances.keys()):
        p2 = distances[dist]
        bended_line.append(Segment(p1, p2))
        p1 = p2
    bended_line.append(Segment(p1, target))
    return bended_line


def merge_lines(lines, glued_inter):
    """
    Takes :
        - a list(Segment), lines (the lines not yet bended)
        - a list( (Point, list(int)) ), glued_inter (the points that are considered as intersections between lines)
    Returns:
        - a list(list(Segment)) (each element within the main list being a "bended" line made of several segments)
    Note : this function adapts the initial segments (lines "skeletons"), such that
    they cross the neighboring intersection points, that have been primarily
    "glued" together. The nintial segment is broken into smaller ones, such
    that the inflexion point is a neighboring intersection. As a result, the
    output is a list of lists of segments, each list of segments corresponding
    to a line.
    """

    where_to_bend = defaultdict(list)
    bended_lines = []
    for inter in glued_inter:
        point = inter[0]  # Point of the intersection
        crossing_lines = inter[1]  # List of the lines' ids
        for crossing_line in crossing_lines:
            where_to_bend[crossing_line].append(point)
    for line_id in where_to_bend.keys():
        bended_line = bend_line(lines[line_id], where_to_bend[line_id])
        bended_lines.append(bended_line)
    for i, line in enumerate(lines):
        if i not in where_to_bend.keys():
            bended_lines.append([line])
    return bended_lines


##############################
# Generation of the stations #
##############################

def generate_stations(bended_lines, variance):
    """
    Creates stations on lines. The output is a list of stations. A station is
    the data of a Point, and a list of tuples containing a line that crosses
    the Point and the position of the Point within this line.
    """
    stations = []
    for j, bended_line in enumerate(bended_lines):
        # we consider a line (possibly made of several segments)
        station_number = 1
        for segment in bended_line:
            source, target = segment.points
            x1, x2, y1, y2 = source[0], target[0], source[1], target[1]
            if station_number == 1:
                approx_x1 = np.random.normal(x1, variance)
                approx_y1 = np.random.normal(y1, variance)
                approx_source = Point(int(approx_x1), int(approx_y1))
                stations.append([approx_source, [(j, station_number)]])
            seg_length = source.distance(target)
            n_stations = math.floor(seg_length/710)
            # we compute the number of stations on the segment (given that the
            # average distance between 2 stations is 710m in Paris)
            dist_between_stations = seg_length/n_stations
            for i in range(1, n_stations):
                station_number += 1
                y = i*dist_between_stations*(y2-y1)/seg_length+y1
                x = i*dist_between_stations*(x2-x1)/seg_length+x1
                x = np.random.normal(x, variance)
                y = np.random.normal(y, variance)
                stations.append([Point(int(x), int(y)), [(j, station_number)]])
            station_number += 1
            stations.append([Point(int(x2), int(y2)), [(j, station_number)]])
    return stations


def points_to_glue(stations, sensitivity):
    """
    This function "glues" stations that are very close from one another,
    according to a sensitivity parameter (distance under which two points will
    be "glued").
    """
    coords = [[int(station[0][0]), int(station[0][1])] for station in stations]
    # coords is a list of lists, each sublist containing the coordinates of a
    # station

    db = DBSCAN(eps=sensitivity, min_samples=2).fit(coords)
    labels = db.labels_
    # labels is a list whose index i contains the cluster id of the i-est
    # station from the input
    clusters = defaultdict(list)
    # clusters is a dictionnary whose keys are the clusters' ids and whose
    # values are the ids of the stations affected to this cluster
    outliers = []
    # outliers is the list of the station ids that have not been affected
    # (not "glued")
    for i, label in enumerate(labels):
        if label != -1:
            clusters[label].append(i)
        else:
            outliers.append(i)
    return outliers, clusters


def glue_stations(outliers, clusters, stations):
    centers = []
    for station_ids in clusters.values():
        # we examine the stations that will be glued together
        lines_crossing = []
        # either a list of tuples (line_id, number), or a list [line_id]
        points = []
        for station_id in station_ids:
            lines_crossing.extend(stations[station_id][1])
            points.append(stations[station_id][0])
        center = np.mean(points, axis=0)
        centers.append([Point(int(center[0]), int(center[1])), lines_crossing])
    for outlier in outliers:
        centers.append(stations[outlier])
    return (centers)
"""
        if len(lines_unique_ids) < len(lines_ids):
            ids_to_del = []
            print("there are duplicates!!")
            lines_ids = np.array(lines_ids)
            for line_unique_id in lines_unique_ids:
                # we check if there was two or more points from the same line that have been glued
                indices = np.where(lines_ids == line_unique_id)[0]
                indices = list(indices)
                indices = sorted(indices, reverse=True)
                if len(indices) > 1:
                    ids_to_del.extend(sorted(indices)[1:])
                    print("indices where duplicates :", indices)
            ids_to_del = (sorted(ids_to_del, reverse=True))
            print("all indices to delete", ids_to_del)
            for id_to_del in ids_to_del:
                del lines_crossing[id_to_del]
            print("new lines_crossing", lines_crossing)

"""
        

def remove_duplicate_lines(stations):
    for station in stations:
        lines_crossing = station[1]
        # list of tuples (line_id, number)

        lines_ids, numbers = zip(*lines_crossing)

        lines_ids = list(lines_ids)
        numbers = list(numbers)
        lines_unique_ids = list(set(lines_ids))

        if len(lines_ids) != len(lines_unique_ids):
            ids_to_del = []

            lines_ids = np.array(lines_ids)
            for line_unique_id in lines_unique_ids:
                # we check if there was two or more points from the same line that have been glued
                indices = np.where(lines_ids == line_unique_id)[0]
                indices = list(indices)
                if len(indices) > 1:
                    ids_to_del.extend(sorted(indices)[1:])
            ids_to_del = (sorted(ids_to_del, reverse=True))
            for id_to_del in ids_to_del:
                del station[1][id_to_del]
    return stations

def merge_stations(stations, glued_inter):
    """
    Given :
        - a list of stations of the form :
            (Point(x, y), [(line_id, point_number)]))
        - a list intersection points of the form :
            (Point(x, y), [line_id, line_id, ...]))
    We merge the stations that are located on the same intersection point, so
    that we obtain stations of the form :
    (Point(x, y), [(line_id, point_number), (line_id, point_number), ...])
    """
    stations_points = np.array([station[0] for station in stations])
    # list of the stations' coordinates
    inter_points = [inter[0] for inter in glued_inter]
    # list of the intersections' coordinates (some of them are expected
    # to match the stations' coordinates)
    ids_to_del = []
    k = 0
    initi = len(stations)
    for inter_point in inter_points:
        # we go through the intersection points ...
        crossing_lines = []
        numbers = []
        station_ids = list(set(np.where(stations_points == inter_point)[0]))
        # we collect the stations whose coordinates match the intersection
        # point
        if len(station_ids) > 1:
            k += 1
            # 2 or more stations share an intersection point : we have to merge
            # them
            for station_id in station_ids:
                crossing_lines.append(stations[station_id][1][0][0])
                numbers.append(stations[station_id][1][0][1])
                ids_to_del.append(station_id)
            stations.append([inter_point, list(zip(crossing_lines, numbers))])
    ids_to_del = sorted(ids_to_del, reverse=True)
    for station_id in ids_to_del:
        del stations[station_id]
    return stations


################################################
# Generation of the hubs and the express lines #
################################################

def compute_hubs(stations):
    """
    Takes :
        - a list( (Point, list((int, int))) ), stations (the stations)
    Returns
        - a list( (Point, int, list((int, int)) ) ), hubs (the hubs)
    
    
    """
    lines_per_station = defaultdict(list)
    # dictionary mapping stations (Points) to the numberof lines that cross it
    point_to_id = {}
    for i, station in enumerate(stations):
        lines_per_station[station[0]] = len(station[1])
        point_to_id[station[0]] = i
    n_stations = len(stations)
    n_hubs = int(0.1*n_stations)
    points = sorted(lines_per_station, key=lines_per_station.get, reverse=True)
    points = points[:n_hubs]
    return [(point, lines_per_station[point], (stations[point_to_id[point]])[1]) for point in points]


def bend_lines(lines, hubs):
    """
    Takes :
        - a list(Segment), lines (some random subway lines)
        - a list((Point, int, list((int, int)))), hubs (some hubs, i.e. a point, an importance,
        a list of lines that cross it with the position of the hub on these lines)
    Returns :
        - a list( list((Point, int, list((int, int)))) ), bended_lines (a list of lists of hubs)
    
    For each line, the function computes the hubs that are "close" according to a
    sensitivity parameter that depends directly one the size of the hub (the
    number of lines that cross it). Then the function orders the hubs based on the distance
    between their projection on the line segment, and the source.
    """
    bended_lines = []

    for line in lines:
        source, target = line.points
        where_to_bend = {}
        for i, hub in enumerate(hubs):
            sensitivity = hub[1]
            point = (hub[0])
            crossing_lines = hub[2]
            dist = line.distance(point)
            if dist < sensitivity*500:
                projection = line.projection(point)
                where_to_bend[i] = source.distance(projection)
        if where_to_bend:
            points_ids = sorted(where_to_bend, key=where_to_bend.get)
            bended_lines.append([[hubs[point_id][0]] + [hubs[point_id][2]] for point_id in points_ids])
    return bended_lines
       

def build_fast_lines(hubs, mu, sigma):
    fast_lines_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    n_fast_lines = len(hubs)
    hubs_points = [hub[0] for hub in hubs]
    point_to_id = {}
    for i, point in enumerate(hubs_points):
        point_to_id[point] = i
    lines = generate_lines(n_fast_lines, mu, sigma)
    fast_lines = bend_lines(lines, hubs)
    return [fast_line for fast_line in fast_lines if len(fast_line) > 3]


def update_compatibilities(stations, fast_lines):

    # no point duplicates, but maybe a point as several times thesame line in its compat
    fast_lines_names = list(ascii_uppercase) 
    stations_points = [station[0] for station in stations]
    for j, fast_line in enumerate(fast_lines):
        for k, hub in enumerate(fast_line):
            i = stations_points.index(hub[0])
            stations[i][1].append((fast_lines_names[j], k))
    return stations


if __name__ == '__main__':
    print("hello")
