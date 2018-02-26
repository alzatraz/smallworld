import networkx as nx
from sympy.geometry import Point


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

def all_shortest_paths_and_lengths(graph):
    shortest_paths = {}
    shortest_lengths = {}
    paths = nx.all_pairs_shortest_path(graph)
    lengths = nx.all_pairs_shortest_path_length(graph)

    for path, length in zip(paths, lengths):
        shortest_paths_from_source = {}
        shortest_lengths_from_source = {}

        source_path = path[0]
        source_length = length[0]

        shortest_paths_dict = path[1]
        shortest_lengths_dict = length[1]

        for target, path_source_target in shortest_paths_dict.items():
            shortest_paths_from_source[target] = [path_source_target, None]
        shortest_paths[source_path] = shortest_paths_from_source

        for target, length_source_target in shortest_lengths_dict.items():
            shortest_paths[source_length][target][1] = length_source_target
    return shortest_paths


def shortest_path(graph, departure, arrival):
    stations = list(graph.nodes())
    departure_station = stations[0]
    arrival_station = stations[0]
    coords = stations[0].coords
    min_dist_departure, min_dist_arrival = coords.distance(departure), coords.distance(arrival)
    for station in stations[1:]:
        coords = station.coords
        dist_departure = coords.distance(departure)
        dist_arrival = coords.distance(arrival)
        if dist_departure < min_dist_departure:
            min_dist_departure = dist_departure
            departure_station = station
        if dist_arrival < min_dist_arrival:
            min_dist_arrival = dist_arrival
            arrival_station = station
    return nx.shortest_path(graph, departure_station, arrival_station)
