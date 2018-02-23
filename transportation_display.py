import matplotlib.pyplot as plt # need sudo apt-get install python3-tk
import numpy as np

def display_segments(lines, intersections, title):
    plt.figure(figsize=(15, 10))
    fig, ax = plt.subplots()
    for segment in lines:
        xs, ys = [], []
        p1, p2 = segment.points
        xs.extend([p1[0], p2[0]])
        ys.extend([p1[1], p2[1]])
        ax.plot(xs, ys)
    if intersections:
        for inter in intersections:
            x, y = inter.coords[0], inter.coords[1]
            ax.scatter(x, y, marker='x')
    plt.title(title)
    plt.savefig('images/adele/'+title+".png")


def display_network(bended_lines, intersections, stations, hubs, fast_lines, title):
    plt.figure(figsize=(15, 10))
    fig, ax = plt.subplots()
    n_stations = len(bended_lines)
    colors = [(np.random.uniform(0, 1, 3)) for _ in range(0, n_stations)]
    for i, bended_line in enumerate(bended_lines):
        color = colors[i]
        xs, ys = [], []
        for segment in bended_line:
            p1, p2 = segment.points
            xs.extend([p1[0], p2[0]])
            ys.extend([p1[1], p2[1]])
        ax.plot(xs, ys, c=color)
    for inter in intersections:
        main_line = inter.compats[0][0]
        x, y = inter.coords[0], inter.coords[1]
        ax.scatter(x, y, marker='x', c=colors[main_line])
    for station in stations:
        point = station.coords
        line_id = station.compats[0][0]
        ax.scatter(point[0], point[1], color=colors[line_id], s=10)
    for hub in hubs:
        point = hub[0]
        importance = hub[1]
        ax.scatter(point[0], point[1], alpha=0.5, s=100*importance)
    colors = [(np.random.uniform(0, 1, 3)) for _ in range(0, len(fast_lines))]
    for j, fast_line in enumerate(fast_lines):
        xs = [hub[0][0] for hub in fast_line]
        ys = [hub[0][1] for hub in fast_line]
        ax.plot(xs, ys, color=colors[j])
    plt.title(title)
    plt.savefig('images/adele/'+title+".png")


def display_path_on_network(departure, arrival, path, network, title):
    lines = network.lines
    n_lines = network.get_n_lines()
    colors = [(np.random.uniform(0, 1, 3)) for _ in range(0, n_lines)]
    for i, line in enumerate(lines):
        stations = line.stations
        coords = [station.coords for station in stations]
        coords = [(coord[0], coord[1]) for coord in coords]
        xs, ys = zip(*coords)
        plt.plot(xs, ys, color=colors[i])
    for station in path:
        plt.scatter(station.coords[0], station.coords[1], color='black', s=40)
    plt.plot([departure[0], path[0].coords[0]], [departure[1], path[0].coords[1]], '--', color='black')
    plt.plot([arrival[0], path[-1].coords[0]], [arrival[1], path[-1].coords[1]], '--', color='black')
    plt.title('Shortest path using the transportation network')
    plt.savefig('images/adele/'+title+'.png')


