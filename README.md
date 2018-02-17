# Data generation project : Small World

## Subway line generation

### Geometry
We generated a complete network which included two types of lines : 'slow' lines (like the Parisian 'métro') and 'fast' lines (like the Parisian 'Météor' or RER).

The 'slow' lines generation was the biggest part of the job. We built them as follows :
- we generated random segments. The number of segments to generate was determined by a truncated gaussian distribution. For each segment, the two extreme points were chosen preferentially in the suburbs of the city, using polar coordinates and a gaussian distribution to determine the length of the radius (for both points) and the angle (for the second point only, approx. a 180° rotation w.r.t the first point, such that the line has good chances to cross the center of the city)
- we computed the approximate intersecions between the segments. First we got the real intersections using the sympy intersection function. Then we looked at the intersections that were close from one another, trying to merge them. To do this task, we used a clustering algorithm called DBSCAN, available in the sklearn package. The algorithm returned clusters of intersection points, and when the cluster conteined more than two points, we pooled the points together at their common barycenter. We also merged the informations of the lines that crossed at these points.
- we bended the initial segments acording to the position of the merged intersection points. Each subway line was then represented by a broken line (i.e. a list of segments)
- we computed the theoretical positions of the stations for each subway line. To compute the position of these theoretical stations, we first put the terminals at the end of the first and last segment of the line (recall that a subway line is a list of segment). Then, we graduated the lines s.t. the theoretical stations were approx. 710 meters away from one another (710 meters being the average distance between two consecutive stations in the parisian Métro)
- we computed the true station position according to the theoretical positions, using a gaussian two-dimensionnal distribution centered on the theoretical position
- we merged the stations that were too close from one another, using again DBSCAN
- we computed the biggest hubs of the network, i.e. the stations were a lot of subway lines were crossing
- we generated the fast lines that should cross these points. First we generated random segments as for the slow lines. Then we computed, for each of these segments, the closest hubs using the sympy distance function (between a point and a line) and a certain distance threshold. We bended the segments s.t. the fast lines cam through the hubs close to them. We kept only the lines that were crossing enough hubs (4). 

### Toponymy

### Schedule 