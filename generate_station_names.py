import re
import numpy as np


def find_country_names():
    page = open("countries.txt", "r")
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


def rectify_unbreakable(name):
    if '&' in name:
        i = name.index('&')
        return name[:i] + " " + name[i+1:]
    else:
        return name

def generate_names(n_stations):
    station_names = set()
    link_words = find_country_names()
    states = list(link_words.keys())
    churches = ["Basilique", "Eglise", "Cathédrale"]
    places = ['Place', 'Rue', 'Avenue', 'Gare', 'Pont', 'Quai']
    names = ['Victor Hugo', 'Guy de Maupassant', 'John F. Kennedy',
             'Franklin D. Roosevelt', 'Gustave Eiffel', 'Adèle Mortier',
             'Louis Cohen', 'Richelieu', 'Marguerite Duras',
             'Nathalie Sarraute', 'Félix Faure', 'Mazarin', 'Danton',
             'Maître&Gims', 'Emmanuel Macron', 'Nicolas Sarkozy',
             'Johnny Hallyday', 'Booba', 'Claude François', 'Voltaire',
             "Jeanne&d'Arc", "Napoléon Bonaparte", "René Descartes",
             "Blaise Pascal", "Molière", "Claude Monet", "Louis Pasteur",
             "Marie Curie", "Marcel Pagnol", "Edit Piaf", "Turgot", "Necker",
             "Sully", "Jean Jaurès", "Auguste Renoir", "Serge Gainsbourg",
             "Georges Brassens", "Lorie", "Florent Pagny", "Céline Dion",
             "Nabilla", "Jean-Paul Sartre", "Boris Vian", "Albert Camus",
             "Charles Aznavour", "Jean Moulin", "Emile Zola", "David Douillet",
             "Jacques Prévert", "Yannick Noah", "Jean Cocteau", "Jean Ferrat",
             "Louis Lumière", "Daniel Balavoine", "Gérard&Philipe",
             "Françoise Dolto", "David Guetta", "Bourvil", "Coluche",
             "Charlemagne", "Zinédine Zidane", "Franck Ribéry",
             "Michel Platini", "Jacques Chirac", "Francis Cabrel",
             "Simone Veil", "Joséphine Baker", "Marlène Dietrich",
             "Anne Frank", "Simone de Beauvoir", "Françoise Sagan",
             "Brigitte Bardot", "Mylène Farmer", "Saint-Louis", "Hugues&Capet",
             "Philippe&Auguste", "François&1er"]
    while len(station_names) < n_stations:
        if (not names) or (not states):
            break
        station_name = ""
        prob_places = np.random.binomial(1, .4)
        place = np.random.choice(places)
        state = np.random.choice(states)
        name = np.random.choice(names)
        if prob_places == 1:
            # something like "Place ..."
            station_name = place
            prob_state = np.random.binomial(1, .3)
            if prob_state == 1:
                # something like "Place de l'Argentine"
                station_name = station_name + " " + link_words[state] \
                               + state
                del states[states.index(state)]
            else:
                prob_saint = np.random.binomial(1, .2)
                if prob_saint == 1:
                    # something like "Place Sainte Marie"
                    name = rectify_unbreakable(name)
                    name = name.split()[0]
                    if name[-1] == 'e':
                        station_name = station_name + " Sainte " + name
                    else:
                        station_name = station_name + " Saint " + name
                else:
                    # something like "Place Edit Piaf"
                    true_name = rectify_unbreakable(name)
                    station_name = station_name + " " + true_name
                    del names[names.index(name)]

        else:
            prob_state = np.random.binomial(1, .2)
            if prob_state == 1:
                prob_saint = np.random.binomial(1, .2)
                if prob_saint == 1:
                    # something like "Notre Dame de l'Argentine"
                    station_name = station_name + " Notre Dame " \
                                    + link_words[state] + state
                else:
                    # something like "Argentine"
                    station_name = state
                del states[states.index(state)]
            else:
                prob_second_name = np.random.binomial(1, 0.5)
                if prob_second_name == 1:
                    # something like "Faidherbe-Chaligny"
                    name1 = name.split()[-1]
                    name1 = rectify_unbreakable(name1)
                    station_name = station_name + name1
                    del names[names.index(name)]

                    name = np.random.choice(names)
                    name2 = name.split()[-1]
                    name2 = rectify_unbreakable(name2)
                    station_name = station_name + "-" + name2
                    del names[names.index(name)]

                else:
                    prob_saint = np.random.binomial(1, .4)
                    if prob_saint == 1:
                        prob_church = np.random.binomial(1, .3)
                        if prob_church == 1:
                            # something like "Eglise Sainte Marie"
                            church_type = np.random.choice(churches)
                            station_name = station_name + church_type
                        name = name.split()[0]
                        # something like "(Eglise)" Saint Maxime
                        if name[-1] == 'e':
                            station_name = station_name + " " + "Sainte " + name
                        else:
                            station_name = station_name + " " + "Saint " + name
                    else:
                        # something like "Louis Lumière"
                        station_name = station_name + rectify_unbreakable(name)
                        del names[names.index(name)]
        station_names.add(station_name)
    return station_names

if __name__ == "__main__":
    names = generate_names(50)
    print(names)
