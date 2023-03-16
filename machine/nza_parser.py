from machine import automata as aut
from os import listdir
from os.path import isfile, join

# f = open("R1.nza", "r", encoding="utf-8").read()


def nadzoru_file_parser(file):
    #Loads a single automaton file and returns a dictionary compatible with our automata library
    events_dict = dict()
    transitions_list = list()
    sources_set = set()
    transitions_dict = dict()
    states_dict = dict()

    events = False
    transitions = False
    states = False
    ready = False

    for line in file.splitlines():
        #Identifying if the parser is reading the data about events, transitions or states
        if line.startswith('["events"] = {'):
            events = True
            transitions = False

        if line.startswith('["transitions"] = {'):
            transitions = True
            events = False

        if line.startswith('["states"] = {'):
            states = True
            transitions = False


        if events:
            if line.startswith('["name"]'):
                line = line.strip('["name"] = ')
                line = line.rstrip('",')
                name = line
            if line.startswith('["controllable"] = false},') or line.startswith('["controllable"] = false}},'):
                controllability = False
                ready = True
            if line.startswith('["controllable"] = true},') or line.startswith('["controllable"] = true}},'):
                controllability = True
                ready = True
            if not (line.startswith('["events"] = {')) and not (line.startswith('["transitions"] = {')) and line.endswith('] = {'):
                line = line.strip('[')
                line = line.rstrip('] = {')
                id = int(line)
            if ready:
                events_dict[id] = aut.Event(name, controllability)
                ready = False


        if transitions:
            events = False
            if line.startswith('["target"] = '):
                line = line.lstrip('["target"] = ')
                line = line.rstrip(',')
                target = line
            if line.startswith('["source"] = '):
                line = line.lstrip('["source"] = ')
                line = line.rstrip(',')
                source = line
            if line.startswith('["event"] = '):
                line = line.lstrip('["event"] = ')
                line = line.rstrip('},')
                event = int(line)
                ready = True
            if ready:
                transitions_list.append(
                    '{s},{e},{t}'.format(s=source, e=event, t=target))
                ready = False


        if states:
            if line.endswith('] = {'):
                line = line.strip('[')
                line = line.rstrip('] = {')
                id = line
            if line.startswith('["initial"] = true'):
                initial = True
                ready = True
            if line.startswith('["initial"] = false'):
                initial = False
                ready = True
            if ready:
                states_dict[int(id)] = aut.State(id, initial)


    # Clean up and dict generation
    for source in transitions_list:
        sources_set.add(source.split(',')[0])

    for source in sources_set:
        transitions_dict[states_dict[int(source)]] = dict()

    for transition in transitions_list:
        s, e, t = transition.split(',')
        s = states_dict[int(s)]
        e = int(e)
        t = states_dict[int(t)]
        transitions_dict[s][events_dict[e]] = t

    return (transitions_dict)


def directory_parser(path, product_or_supervisor):
    #Loads every nza file inside a directory and generates their automata
    automata_list = list()

    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    for file in onlyfiles:
        if file.endswith('.nza'):
            if product_or_supervisor:
                print('Loaded a product system\'s automaton from file: ', file)
            
            else:
                print('Loaded a modular supervisor automaton from file: ', file)
            file_path = path + '/' + file
            
            f = open(file_path, "r", encoding="utf-8").read()
            transitions = nadzoru_file_parser(f)
            automata_list.append(aut.Automaton(
                file.rstrip('.nza'), transitions, product_or_supervisor))
        
        else:
            print('File', file, 'has a type not supported yet')

    return (automata_list)
