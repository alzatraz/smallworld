import sympy
from sympy import *
from sympy.geometry import *
from sympy.plotting import plot
import numpy as np
import math

def generate_n_lines():
    n_lines = 0
    mu, sigma = 10, 3 
    while n_lines == 0:
        n_lines = np.random.normal(mu, sigma)
        print(n_lines)
    return (round(n_lines))

def generate_lines(n_lines):
    mu, sigma = 5000, 1500 
    lines = []
    for _ in range(0, n_lines):
        rhos = np.random.normal(mu, sigma, 2)
        theta0 = np.random.uniform(0, 2*math.pi)
        theta1 = np.random.normal(theta0-math.pi, math.pi/3)
        source = Point(int(rhos[0]*math.cos(theta0)), int(rhos[0]*math.sin(theta0)))
        target = Point(int(-rhos[1]*math.cos(theta1)), int(-rhos[1]*math.sin(theta1)))
        line = Segment(source, target)
        lines.append(line)
    return lines

def find_intersections(lines):
    intersections = []
    for i in range(0, len(lines)-1):
        for j in range(i+1, len(lines)):
            line1 = lines[i]
            line2 = lines[j]
            inter = intersection(line1, line2)
            if inter:
                point = inter[0]
                intersections.append((point, i, j))
    return intersections

def generate_stations(lines, intersections):
    stations = {}
    for inter in intersections

if __name__ == "__main__":