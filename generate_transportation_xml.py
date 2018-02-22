from rdflib import *


def write_preamble(file, tab):
    file.write('<?xml version="1.0"?>\n')

    file.write('<rdf:RDF\n')
    file.write('xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n')
    file.write('xmlns:trspt="http://smallworld.com/transportation#"\n')
    file.write('xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#">\n')
    file.write(tab + '<rdf:Description\n')
    file.write(tab + '  ' + 'rdf:about="http://smallworld.com/transportation">\n')
    file.write(tab + '  ' + '<trspt:lines rdf:parseType="Collection">\n')

def write_line(i, line, file, tab):
    if type(i) == int:
        path_name = 'M'+str(i)
        line_name = 'Métro Ligne ' + str(i)
        speed = 'slow'
    else:
        path_name = 'RER'+i
        line_name = 'RER Ligne ' + i
        speed = 'fast'
    n_stations = str(len(line))
    file.write(tab + '<rdf:Description rdf:about="http://smallworld.com/transportation/' + path_name + '"\n')
    tab = tab + '  '     
    file.write(tab + 'xmlns:line="http://smallworld.com/transportation/' + path_name + '#">\n')
    file.write(tab + '<line:name>'+line_name+'</line:name>\n')
    file.write(tab + '<line:speed>'+speed+'</line:speed>\n')
    file.write(tab + '<line:number_of_stations>'+n_stations+'</line:number_of_stations>\n')    
    file.write(tab + '<line:stations rdf:parseType="Collection">\n')
    return path_name 

def write_coords(point, file, tab):
    x, y = point[0], point[1]
    file.write(tab + '<geo:Point>\n')
    file.write(tab + '  ' + '<geo:lat>' + str(x) + '</geo:lat>\n')
    file.write(tab + '  ' + '<geo:long>' + str(y) + '</geo:long>\n')
    file.write(tab + '</geo:Point>\n')


def write_station(path_name, station, file, tab):
    point, number, name, schedule_forward, schedule_backward = station
    file.write(tab + '<rdf:Description\n')
    tab = tab + '  '
    file.write(tab + 'rdf:about="http://www.smallworld.com/transportation/'+path_name+'/'+str(number)+'"\n')
    file.write(tab + 'xmlns:station="http://smallworld.com/transportation/'+path_name+'/'+str(number)+'#">\n')
    write_coords(point, file, tab)
    file.write(tab + '<station:name>'+name+'</station:name>\n')
    file.write(tab + '<station:number>'+str(number)+'</station:number>\n')
    write_schedule('forward', schedule_forward, file, tab)
    write_schedule('backward', schedule_forward, file, tab)


def write_schedule(direction, schedule, file, tab):
    file.write(tab + '<station:schedule_'+direction+'>\n')    
    file.write(tab + ' ' + '<rdf:Seq>\n')
    for time in schedule:
        file.write(tab + '    ' + '<rdf:li>'+time_tuple_to_string(time)+'</rdf:li>\n')
    file.write(tab + '  ' + '</rdf:Seq>\n')
    file.write(tab+ '</station:schedule_'+direction+'>\n') 

def complete_with_zero(i):
    if i in range(0, 10):
        return ('0' + str(i))
    return str(i)

def time_tuple_to_string(time_tuple):
    string_time = ""
    for time in time_tuple:
        string_time = string_time + complete_with_zero(time) + ":"
    return string_time[:-1]

def generate_xml(lines_dict):
    tab = '  '
    file = open('transportation.xml','w') 
    write_preamble(file, tab)
    for i, line in lines_dict.items():
        path_name = write_line(i, line, file, tab*3)
        for station in line:
            write_station(path_name, station, file, tab*5)
            file.write(tab*5 + '</rdf:Description>\n')
        file.write(tab*4 + '</line:stations>\n')
        file.write(tab*3 + '</rdf:Description>\n')
    file.write(tab*2 + '</trspt:lines>\n')
    file.write(tab + '</rdf:Description>\n')
    file.write('</rdf:RDF>')
    file.close() 



def generate_rdf(lines_dict):
    g = Graph()
    schema = Namespace('http://schema.org/')
    smallworld = 'http://smallworld.org/'
    for i, stations in lines_dict.items():
        if type(i) == int:
            line_name = 'Métro Ligne ' + str(i)
            line_path = 'M' + str(i)
        else:
            line_name = 'RER Ligne ' + i
            line_path = 'RER' + i
        line_path = smallworld + 'lines/' + line_path + '/'
        line = URIRef(line_path)
        g.add((line, schema.name, Literal(line_name)))
        print(stations)
        for j, station in enumerate(stations):
            point, number, name, schedule_forward, schedule_backward = station
            coords = BNode()
            g.add((coords, schema.latitude, Literal(point[0])))
            g.add((coords, schema.longitude, Literal(point[1])))
            station = URIRef(smallworld + 'stations/' + name + '/')
            g.add((station, schema.geo, coords))
            g.add((line, schema.containsPlace, station))
            g.add((station, schema.name, Literal(name)))
            # g.add((line,)) order
            departure_forward, departure_backward = BNode(), BNode()
            g.add((line, schema.event, departure_forward))
            g.add((line, schema.event, departure_backward))
            for time_tuple in schedule_forward:
                g.add((departure_forward, schema.subEvent, departure_forward))
                time = time_tuple_to_string(time_tuple)
                g.add((departure_forward, schema.startDate, Literal(time)))
            for time_tuple in schedule_backward:
                g.add((departure_backward, schema.subEvent, departure_forward))
                time = time_tuple_to_string(time_tuple)
                g.add((departure_backward, schema.startDate, Literal(time)))
    return g



if __name__ == "__main__":
    lines_dict = {0 : [[(0, 0), 5, 'Châtelet', [(2, 30, 1), (3, 14, 20), (10, 15, 4), (11, 15, 41)], [(1, 5, 4), (1, 2, 74), (15, 4, 8), (4, 15, 4)]], [(0, 1), 4, 'Pont-Neuf', [(7,4, 8), (7, 9, 54)], [(4, 74, 5), (4, 54, 21)]]]}
    g = generate_rdf(lines_dict)
    print(g.serialize())
    g.serialize("test.rdf")