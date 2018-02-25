import re
import numpy as np
import csv



####################
# Import functions #
####################

def fetch_countries():
    page = open("data/countries.txt", "r")
    page = str(page.read())

    country_names = {}
    link_words_to_search = ['du ', "d'", "l'", "(la|La) ", "(le|Le) "]

    link_words_to_enter = {'du ': 'du ', "l'": "de l'", "d'": "d'",
                           "(la|La) ": "de la ", "(le|Le) ": "du "}
    for link_word in link_words_to_search:
        pattern = link_word + "([A-Z])((([a-z])*(é|è|ë|ï)*([a-z])*)+)"
        occurrences = re.findall(pattern, page)
        if link_word in ['du ', "l'", "d'"]:
            k = 0
        else:
            k = 1
        for occurrence in occurrences:
            country_name = occurrence[k] + occurrence[k+1]
            if country_name not in country_names.keys() and len(country_name) >= 4:
                country_names[country_name] = link_words_to_enter[link_word]
    return country_names

def fetch_names():
    names = {}
    file = open("data/names.txt", "r")
    file = str(file.read())
    file = file.split("\n")
    for item in file:
        name, gender = item.split(', ')
        names[name] = gender
    return names


def fetch_first_names():
    first_names = {}
    file = open("data/first_names.csv", "r", encoding = "ISO-8859-1")
    for line in file:
        if 'french' in line:
            line = line.split(';')
            name = line[0]
            gender = restrict_gender(line[1])
            if '(' in name:
                i = name.index('(')
                name = name[:i]
            name = name.capitalize()
            first_names[name] = gender
    return first_names


####################
# Helper functions #
####################

def restrict_gender(gender):
    if ',' in gender:
        prob_f = np.random.binomial(1, .5)
        if prob_f:
            return gender[0]
        else:
            return gender[2]
    return gender


def rectify_unbreakable(name):
    if '&' in name:
        i = name.index('&')
        return name[:i] + " " + name[i+1:]
    else:
        return name

def take_first_if_composed(name):
    if '-' in name:
        i = name.index('-')
        return name[:i]

def drop_first_name(name):
    parts = name.split()
    return parts[-1]

def build_saint_name(first_name, first_names_to_gender):
    gender = first_names_to_gender[first_name]
    saint = ""
    if gender == 'm':
        saint = "Saint"
    else:
        saint = "Sainte"
    return saint + " " + first_name


###################
# Name generation #
###################

def generate_names(n_stations):
    station_names = []

    churches = ["Basilique", "Eglise", "Cathédrale"]
    places = ['Place', 'Rue', 'Avenue', 'Gare', 'Pont', 'Quai']

    country_to_link = fetch_countries()
    countries = list(country_to_link.keys())

    names_to_gender = fetch_names()
    names = list(names_to_gender.keys())

    first_names_to_gender = fetch_first_names()
    first_names = list(first_names_to_gender.keys())
    while len(station_names) < n_stations:
        station_name = ""
        prob_place = np.random.binomial(1, .4)
        if prob_place:
            # something like Place ...
            place = np.random.choice(places)
            station_name = station_name + place + " "
            prob_name = np.random.binomial(1, .4)
            if prob_name:
                prob_saint = np.random.binomial(1, .1)
                if prob_saint:
                    # something like Place Sainte Marie
                    first_name = np.random.choice(first_names)
                    saint_name = build_saint_name(first_name,
                                                  first_names_to_gender)
                    station_name = station_name + saint_name
                    del first_names[first_names.index(first_name)]
                else:
                    # something like Place (Marcel) Pagnol
                    name = np.random.choice(names)
                    prob_drop_first_name = np.random.binomial(1, .3)
                    if prob_drop_first_name:
                        true_name = drop_first_name(name)
                        true_name = rectify_unbreakable(true_name)
                    else:
                        true_name = rectify_unbreakable(name)
                    station_name = station_name + true_name
                    del names[names.index(name)]
            else:
                # something like Place de l'Argentine
                country = np.random.choice(countries)
                link = country_to_link[country]
                station_name = station_name + link + country
                del countries[countries.index(country)]
        else:
            # something like Gustave Eiffel, Saint Basile, Argentine ...
            prob_name = np.random.binomial(1, .7)
            if prob_name:
                # something like Saint Basile, Felix Faure...
                prob_saint = np.random.binomial(1, .2)
                if prob_saint:
                    # something like (Cathédrale) Saint Basile
                    first_name = np.random.choice(first_names)
                    station_name = build_saint_name(first_name,
                                                    first_names_to_gender)
                    del first_names[first_names.index(first_name)]
                    prob_church = np.random.binomial(1, .3)
                    if prob_church:
                        church = np.random.choice(churches)
                        station_name = church + " " + station_name
                else:
                    prob_2_names = np.random.binomial(1, .6)
                    if prob_2_names:
                        # something like Faidherbe-Chaligny
                        name1 = np.random.choice(names)
                        del names[names.index(name1)]
                        name2 = np.random.choice(names)
                        del names[names.index(name2)]
                        true_name1 = drop_first_name(name1)
                        true_name2 = drop_first_name(name2)
                        true_name1 = rectify_unbreakable(true_name1)
                        true_name2 = rectify_unbreakable(true_name2)
                        
                        station_name =  true_name1 + "-" + true_name2
                    else:
                        # something like Georges Brassens
                        name = np.random.choice(names)
                        true_name = rectify_unbreakable(name)
                        station_name = true_name
                        del names[names.index(name)]

            else:
                # something like Argentine
                country = np.random.choice(countries)
                station_name = country
                del countries[countries.index(country)]
        station_names.append(station_name)
    return station_names


def add_names(names, stations):
    for i, name in enumerate(names):
        stations[i].name = name
    stations_points = [station.coords for station in stations]
    return stations



if __name__ == "__main__":
    names = generate_names(150)
    print(names)
