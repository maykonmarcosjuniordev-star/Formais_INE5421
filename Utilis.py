"""
Padrão da entrada

<número de estados>;<estado inicial>;{<estados finais>};{<alfabeto>};<transições>

Os estados são sempre identificados com letras maiúsculas.
As transições são da forma <estado origem>,<simbolo do alfabeto>,<estado destino>.
"""

DEBUG_S = False
DEBUG_F = False
TESTE = 0
from collections import defaultdict

class Automaton:
    def __init__(self, num_states:int, initial_state:str,
                 final_states:set[str], alphabet:set[str],
                 transitions:list[tuple[str]]):
        self.num_states = num_states
        self.initial_state = initial_state
        self.final_states = final_states
        self.alphabet = alphabet
        self.transitions_tuple = transitions
        self.transitions_dict = defaultdict(defaultdict(list))
        for src, sym, dst in transitions:
            self.transitions_dict[src][sym].append(dst)
    
    def __str__(self):
        output = f"Automaton(Nstates = {self.num_states}, Alphabet = {self.alphabet}, Initial State = {self.initial_state}, Final States = {self.final_states}\nTransitions:\n"
        for src, sym, dst in self.transitions_tuple:
            output += f"{src} -> {dst} by {sym}\n"
            

def read_input(entry:str=None) -> tuple[int, str, set[str], set[str], list[tuple[str]]]:
    '''
    Lê a entrada no formato especificado.
    '''
    if not entry:
        entry = input().split(";")
    else:
        entry = (entry.strip()).split(";")
    num_states = int(entry[0])
    initial_state = entry[1]
    alphabet = set(entry[3].strip("{}").split(","))
    if initial_state[0] == "{":
        final_states = set('{' + t + '}' for t in entry[2].strip("{}").split("},{"))
        transitions = []
        for t in entry[4:]:
            src, rest = t.split("},")
            sym, dst = rest.split(",{")
            transitions.append((src + '}', sym, '{' + dst))
    else:
        final_states = set(entry[2].strip("{}").split(","))
        transitions = [tuple(t.split(",")) for t in entry[4:]]
    if DEBUG_S:
        global TESTE
        TESTE += 1
        print("-------------\nTESTE", TESTE, "-  S")
        table = make_table(transitions, alphabet)
        print_table(table)
    # automaton = Automaton(num_states, initial_state, final_states, alphabet, transitions)
    # print(automaton)
    return num_states, initial_state, final_states, alphabet, transitions


def print_output(new_transitions: defaultdict, new_initial_state:str,
                 new_final_states:set, alphabet:set) -> None:
    '''
    Imprime o AFD resultante.
    '''
    # print(sorted(new_transitions.items()), end="\n\n")
    output_string = f"{len(new_transitions.keys())};"
    output_string += new_initial_state + ";"
    final_states_matrix = ["".join(j for j in i) for i in sorted(new_final_states)]
    output_string += "{" + ",".join(final_states_matrix) + "};"
    output_string += "{" + ",".join(sorted(alphabet)) + "}"
    for state, transitions in sorted(new_transitions.items()):
        for symbol, next_state in sorted(transitions.items()):
            output_string += f";\n{state} -- {symbol} --> {next_state}"
    print(output_string, end="\n\n")
    
    if DEBUG_F:
        new_af = read_input(output_string)
        table = make_table(new_af[4], new_af[3])
        global TESTE
        print("\n-------------\nTESTE", TESTE, "-  F")
        print_table(table)
        print("-------FIM DO TESTE------\n")
        TESTE += 1
        

def make_table(transitions:list[tuple[str]], alphabet:set[str]) -> defaultdict[dict[str]]:
    '''
    Cria uma tabela de transições a partir da entrada.
    '''
    table = defaultdict(dict)
    src_states = set(i[0] for i in transitions)
    dst_states = set(i[2] for i in transitions)
    states = src_states.union(dst_states)
    for t in transitions:
        src = t[0]
        sym = t[1]
        dst = ",".join(t[2:])
        if sym in table[src]:
            table[src][sym] += "," + dst
        else:
            table[src][sym] = dst
    for state in states:
        for symbol in alphabet:
            if symbol not in table[state]:
                table[state][symbol] = "-"
    return table

def print_table(table: defaultdict[dict[str]]):
    '''
    Imprime a tabela de transições.
    '''
    output_string = "\n     TABELA DE TRANSIÇÕES     \n"
    table_set = sorted(table.items())
    output_string += "Estado   "
    simbols = sorted(table_set[0][1].keys())
    for i in simbols:
        output_string += f"    {i}       "
    output_string += "\n---------------------------------------------------\n"
    for state, transitions in table_set:
        src = state.ljust(7)
        output_string += src
        for sym in simbols:
            destination = transitions[sym].ljust(6)
            output_string += destination.rjust(12)
        output_string += "\n"
    print(output_string)
