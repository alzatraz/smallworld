# Data generation project : Small World

## Subway line generation

### Geometry
We generated a complete network which included two types of lines : 'slow' lines (like the Parisian 'métro') and 'fast' lines (like the Parisian 'Météor' or RER).

The 'slow' lines generation was the biggest part of the job. We built them as follows :
1. we generated **random segments for the slow lines**. The number of segments to generate was determined by a truncated gaussian distribution. For each segment, the two extreme points were chosen preferentially in the suburbs of the city, using polar coordinates and a gaussian distribution to determine the length of the radius (for both points) and the angle (for the second point only, approx. a 180° rotation w.r.t the first point, such that the line has good chances to cross the center of the city)
2. we computed the **approximate intersecions between the segments**. First we got the real intersections using the sympy intersection function. Then we looked at the intersections that were close from one another, trying to merge them. To do this task, we used a clustering algorithm called DBSCAN, available in the sklearn package. The algorithm returned clusters of intersection points, and when the cluster conteined more than two points, we pooled the points together at their common barycenter. We also merged the informations of the lines that crossed at these points.
3. we **bended the initial segments** acording to the position of the merged intersection points. Each subway line was then represented by a broken line (i.e. a list of segments)
4. we computed the **theoretical positions of the stations** for each subway line. To compute the position of these theoretical stations, we first put the terminals at the end of the first and last segment of the line (recall that a subway line is a list of segment). Then, we graduated the lines s.t. the theoretical stations were approx. 710 meters away from one another (710 meters being the average distance between two consecutive stations in the parisian Métro)
5. we computed the **true positions of the stations** according to the theoretical positions, using a gaussian two-dimensionnal distribution centered on the theoretical position
6. we **merged the stations** that were too close from one another, using again DBSCAN

The 'fast' lines generation was easier :
1. we computed the **biggest hubs** of the network, i.e. the stations were a lot of subway lines were crossing
2. we generated **random segments** as for the slow lines.
3. we computed the **closest hubs w.r.t each segment**. To this aim, we usedd the sympy distance function (distance between a point and a line), and considered a hub was 'close enough' from a line if the distance between the hub and the line was below and a certain threshold.
4. We **bended the segments** s.t. the fast lines came through the hubs close to them.
5. we kept only the lines that were crossing enough hubs (typically 4). 

### Toponymy
We generated random names for the stations we created. This implied to have a database for the names to combine together, and a method to combine names s.t. the combination makes sense.
To create the databsases, we used differents ressources:
- for the country names, we scrapped a Wikipedia page (https://fr.wikipedia.org/wiki/Liste_des_pays_du_monde), using regular expressions.This allowed to capture, in addition to the country names themselves, the way to combine them (the article 'of' in French depends on the grammatical gender, and countries can have unexpected genders...).
- for the famous people names, we created a list manually
- for the first names (that appear in station names like Saint Marcel), we used a dataset provided by Data.gouv.fr (https://www.data.gouv.fr/fr/datasets/liste-de-prenoms/). The advantage of this dataset was that it also contained gender informations, which was useful to determine easily which of "Sainte Marie" and "Saint Marie" was correct. Since the dataset was quite huge, we just selected names that were labeled as 'french'

To combine the different elements, we thought of a station name as the result of a probabilistic tree. The output of our tree could roughly have four forms:
- a urban element plus a name (famous person or saint something) : Place Emile Zola
- a urban element plus a country name : Place de la Grèce
- a simple name (famous person or saint something or religious place plus saint something) : Emile Zola
- a simple country name : Grèce

A more detailed version of this kind of grammar can be found above, using regular expressions.

```
Ɛ ...
│
└───... (Place|Rue|Avenue|Gare|Pont|Quai) ...
│   │
│   └───... Saint(e|Ɛ)...
│   │   │
│   │   └───... Sainte (Marie|Françoise|Emma...)
│   │   │   
│   │   └───... Saint (Joseph|Marc|Louis...)
│   │
│   └───... (Marcel|Emile|Guy...|Ɛ) (Pagnol|Zola|de Maupassant...)
│   │   │
│   │   └───... (Marcel Pagnol|Emile Zola|Guy de Maupassant...)
│   │   │   
│   │   └───... (Pagnol|Zola|Maupassant...)
│   │ 
│   └───... (de l'Argentine|du Pérou|de la Suisse...)
│   
└───... Ɛ ...
    │
    └───... (Basilique|Eglise|Cathédrale|Ɛ) (Saint(e|Ɛ)|Ɛ) (Marcel|Emile|Guy...) (Pagnol|Zola|de Maupassant...|Ɛ)
    │   │   
    │   └───... (Basilique|Eglise|Cathédrale|Ɛ) Saint(e|Ɛ) (Marcel| Emilie...)
    │   │   │
    │   │   └───(Basilique|Eglise|Cathédrale) Saint(e|Ɛ) (Marcel| Emilie...)
    │   │   │   │
    │   │   │   └───(Basilique|Eglise|Cathédrale) Sainte (Emilie|Clothilde|Lucie...)
    │   │   │   │
    │   │   │   └───(Basilique|Eglise|Cathédrale) Saint (Marcel|Mathieu|Louis...)
    │   │   │
    │   │   └───Saint(e|Ɛ) (Marcel|Emilie...)
    │   │       │
    │   │       └───Sainte (Emilie|Clothilde|Lucie...)
    │   │       │
    │   │       └───Saint (Marcel|Mathieu|Louis...)
    │   │
    │   └───... (Marcel Pagnol|Guy de Maupassant|Olympe de Gouges...)
    │   │
    │   └───... (Pagnol-Maupassant|Zola-Pagnol...)
    │
    └───... (Pérou|Argentine|Suisse...)
```

We had to do small tricks for names that were kind of unbreakable, like "Jeane d'Arc" for instance ("Rue d'Arc" is not really correct). We added some fanciful names to the "famous people" section, for instance national icons like Booba, Nabilla, Johny Hallyday or Mylène Farmer.

### Schedule 
For each station, we had to generate a schedule, i.e. a list of times when a train arrives at the station, in one direction or the other. We thus had to generate a 'forward' schedule and a 'backward' schedule. For each subway line and given the stations' coordinates, we proceeded as follows:
1. we computed the distances between each adjacent stations, and then the time to go from one station to the next one, depending on the speed on the line (recall that we have 'slow' lines and 'fast' lines)
2. we generated the first departure and arrival times (backward and forward) at the terminals, depending of the day (+1 for the last departure/arrival if we are Friday or Saturday), and following a uniform distribution (between 5:30 and 6:00 te morning, 0:30 and 1:30 the night)
3. as many times as needed (i.e. until we reached the last departure time), we generated new departures from the terminals with a variable frequency (more frequent the morning and the evenning), and propagated the times using the time intervals computed in the first step. We allowed small gausain variations that we added to the time intervals (approx. 10 seconds)
