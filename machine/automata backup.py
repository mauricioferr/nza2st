class State():
    def __init__(self, name: str, initial=False):
        self.initial = initial
        self.name = name


class Event():
    def __init__(self, name: str, control=False):
        self.name = name
        self.control = control


class Automaton():
    def __init__(self, name: str, transitions: dict, product_or_supervisor=False):
        self.transitions = transitions
        self.product_or_supervisor = product_or_supervisor
        self.name = name

    def returnStates(self):
        initial = set()
        other_states = set()

        for k in self.transitions.keys():
            if k.initial:
                initial.add(self.name+'_'+k.name)
            else:
                other_states.add(self.name+'_'+k.name)
        return(initial, other_states)

    def returnEvents(self):
        controllable = set()
        uncontrollable = set()

        for k in self.transitions.keys():
            for v in self.transitions[k].keys():
                if v.control:
                    controllable.add(v.name)
                else:
                    uncontrollable.add(v.name)
        return(controllable, uncontrollable)

    def returnTransitions(self):
        text = ''
        text2 = ''
        for k in self.transitions.keys():
            state = self.name+'_'+k.name
            for e in self.transitions[k].keys():
                if e.control:
                    if self.product_or_supervisor:
                        text2 += 'IF '+state+' AND '+e.name+' AND NOT d_'+e.name+' THEN\n'
                        text2 += '\t'+self.name+'_' + \
                            self.transitions[k][e].name+' S= TRUE;\n'
                        text2 += '\t'+state+' R= TRUE;\n'
                        text2 += '\t'+e.name+' := ('+state+' AND NOT d_'+e.name+');\n'
                        text2 += 'END_IF\n'
                    else:
                        text2 += 'IF '+state+' AND '+e.name + ' THEN\n'
                        text2 += '\t'+self.name+'_' + \
                            self.transitions[k][e].name+' S= TRUE;\n'
                        text2 += '\t'+state+' R= TRUE;\n'
                        text2 += 'END_IF\n'
                else:
                    text += 'IF '+state+' AND '+e.name+' THEN\n'
                    text += '\t'+self.name+'_' + \
                        self.transitions[k][e].name+' S= TRUE;\n'
                    text += '\t'+state+' R= TRUE;\n'
                    text += 'END_IF\n'
        return(text, text2)

    def returnDisablementsFromSingleAutomaton(self):
        events_dict = dict()
        all_states = set()
        for k in self.transitions.keys():
            all_states.add(self.name+'_'+k.name)
            for e in self.transitions[k].keys():
                if e.control:
                    if e.name not in events_dict.keys():
                        events_dict[e.name] = set()
                        events_dict[e.name].add(self.name+'_'+k.name)
                    else:
                        events_dict[e.name].add(self.name+'_'+k.name)

        complementary_set = dict()
        for e in events_dict.keys():
            complementary_set[e] = all_states-events_dict[e]

        return(complementary_set)


def variableInitialization(automata: list):
    initial_states = set()
    other_states = set()
    controllable_events = set()
    uncontrollable_events = set()
    text = ''
    text2 = ''

    for automaton in automata:
        [initial, other] = automaton.returnStates()
        [controllable, uncontrollable] = automaton.returnEvents()
        initial_states.update(initial)
        other_states.update(other)
        controllable_events.update(controllable)
        uncontrollable_events.update(uncontrollable)

    for s in initial_states:
        text = text + s + ':BOOL:=TRUE;\n'
    for s in other_states:
        text = text + s + ':BOOL;\n'
    for e in controllable_events:
        text = text + e + ':BOOL;\n'
        text = text + 'd_' + e + ':BOOL;\n'

    for e in uncontrollable_events:
        text = text + e + ':BOOL;\n'
    counter1 = 1
    for e in uncontrollable_events:
        text += 'R_TRIGGER'+str(counter1)+':R_TRIG;\n'
        text2 += 'R_TRIGGER'+str(counter1)+'(CLK:= SUBSTITUIR);\n'
        text2 += e+':='+'R_TRIGGER'+str(counter1)+'.Q;\n'
        counter1 += 1

    return(text, text2)


def transitionsDeclaration(automata: list):
    product_uncontrollable = ''
    product_controllable = ''
    supervisor_controllables = ''
    supervisor_uncontrollables = ''
    for automaton in automata:
        uncontrollable, controllable = automaton.returnTransitions()
        if automaton.product_or_supervisor:
            product_controllable += controllable
            product_uncontrollable += uncontrollable
        else:
            supervisor_controllables += controllable
            supervisor_uncontrollables += uncontrollable

    return(product_uncontrollable, supervisor_uncontrollables, product_controllable, supervisor_controllables)


def disablementsDeclaration(automata: list):
    disabled_dict = dict()
    for automaton in automata:
        if not automaton.product_or_supervisor:
            automaton_disablements = automaton.returnDisablementsFromSingleAutomaton()
            for e in automaton_disablements.keys():
                try:
                    new_items = automaton_disablements[e]
                    old_set = disabled_dict[e]
                    old_set.update(new_items)
                    disabled_dict[e] = old_set
                except KeyError:
                    disabled_dict[e] = automaton_disablements[e]

    text = ''
    for e in disabled_dict.keys():
        text += 'd_'+e + ' := '

        keys = sorted(disabled_dict[e])
        for s in keys:
            if s == keys[-1]:
                text += s + '\n'
            else:
                text += s + ' OR '
    return(text)

"""
s0 = State('0', True)
s1 = State('1')
s2 = State('2')

b1 = Event('B1')
b1_leaving = Event('B1_LEAVING')
b1_left = Event('B1_LEFT')
g1 = Event('G1')
g1_leaving = Event('G1_LEAVING')
g1_left = Event('G1_LEFT')

b2 = Event('B2')
b2_leaving = Event('B2_LEAVING')
b2_left = Event('B2_LEFT')
g2 = Event('G2')
g2_leaving = Event('G2_LEAVING')
g2_left = Event('G2_LEFT')

e1_on = Event('E1_ON', True)
e1_off = Event('E1_OFF', True)

e2_on = Event('E2_ON', True)
e2_off = Event('E2_OFF', True)

e3_on = Event('E3_ON', True)
e3_off = Event('E3_OFF', True)

e4_on = Event('E4_ON', True)
e4_off = Event('E4_OFF', True)

b1_start = Event('B1_START', True)
b1_partial = Event('B1_PARTIAL', True)
b1_finished = Event('B1_FINISHED', True)
g2_start = Event('G2_START', True)
g2_partial = Event('G2_PARTIAL', True)
g2_finished = Event('G2_FINISHED', True)

s3_off = Event('S3_OFF')
s4_off = Event('S4_OFF')


sensor1 = {s0: {b1: s1, g1: s2}, s1: {b1_leaving: s1,
                                      b1_left: s0}, s2: {g1_leaving: s2, g1_left: s0}}

sensor2 = {s0: {b2: s1, g2: s2}, s1: {b2_leaving: s1,
                                      b2_left: s0}, s2: {g2_leaving: s2, g2_left: s0}}

sensor_saida = {s0:{s3_off:s0,s4_off:s0}}
esteira1 = {s0: {e1_on: s1}, s1: {e1_off: s0}}
esteira2 = {s0: {e2_on: s1}, s1: {e2_off: s0}}
esteira3 = {s0: {e3_on: s1}, s1: {e3_off: s0}}
esteira4 = {s0: {e4_on: s1}, s1: {e4_off: s0}}

robo = {s0: {b1_start: s1, g2_start: s2}, s1: {b1_partial: s1,
                                               b1_finished: s0}, s2: {g2_partial: s2, g2_finished: s0}}


e1 = {s0:{b1:s1,g1:s1,b1_leaving:s0,g1_leaving:s0},s1:{b1:s1,g1:s1,e1_off:s1,b1_leaving:s0,g1_leaving:s0}}



G1 = Automaton('G2', sensor1, True)
G2 = Automaton('G2', sensor2, True)
G3 = Automaton('G3', sensor_saida, True)
G4 = Automaton('G1', esteira1, True)
G5 = Automaton('G5', esteira2, True)
G6 = Automaton('G6', esteira3, True)
G7 = Automaton('G7', esteira4, True)
G8 = Automaton('G8', robo, True)

E1 = Automaton('E1', e1, False)

automata = [G1,G2,G3,G4,G5,G6,G7,G8, E1]
print(type(automata))
automata = [G1,G4,E1]

A, B = variableInitialization(automata)
C,D,F,G = transitionsDeclaration(automata)
E = disablementsDeclaration(automata)

print('***********A************')
print(A)
print('***********B************')
print(B)
print('***********C************')
print(C)
print('***********D************')
print(D)
print('***********E************')
print(E)
print('***********F************')
print(F)
print('***********G************')
print(G)"""

