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
            x, y = inter[0][0], inter[0][1]
            ax.scatter(x, y, marker='x')
    plt.title(title)
    plt.savefig(title+".png")


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
        main_line = inter[1][0]
        x, y = inter[0][0], inter[0][1]
        ax.scatter(x, y, marker='x', c=colors[main_line])
    for station in stations:
        point = station[0]
        line_id = station[1][0][0]
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
    plt.savefig(title+".png")

