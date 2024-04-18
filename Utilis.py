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

def read_input(entry:str=None) -> tuple[set[str], str, set[str], set[str], list[tuple[str]]]:
    '''
    Lê a entrada no formato especificado.
    '''
    if not entry:
        entry = input().split(";")
    else:
        entry = (entry.strip()).split(";")
    num_states = int(entry[0])
    initial_state = entry[1]
    final_states = set(entry[2].strip("{}").split(","))
    alphabet = set(entry[3].strip("{}").split(","))
    transitions = [tuple(t.split(",")) for t in entry[4:]]
    if DEBUG_S:
        global TESTE
        TESTE += 1
        print("-------------\nTESTE", TESTE, "-  S")
        table = make_table(transitions, alphabet)
        print_table(table)
    return num_states, initial_state, final_states, alphabet, transitions


def print_output(new_transitions: defaultdict, new_initial_state:str,
                 new_final_states:set, alphabet:set) -> None:
    '''
    Imprime o AFD resultante.
    '''
    # print(sorted(new_transitions.items()), end="\n\n")
    output_string = f"{len(new_transitions.keys())};"
    output_string += "{" + "".join(sorted(new_initial_state)) + "};"
    final_states_matrix = ["".join(j for j in i) for i in sorted(new_final_states)]
    output_string += "{{" + "},{".join(final_states_matrix) + "}};"
    output_string += "{" + ",".join(sorted(alphabet)) + "}"
    for state, transitions in sorted(new_transitions.items()):
        for symbol, next_state in sorted(transitions.items()):
            src = "{" + ''.join(state) +"}"
            dst = "{" + ''.join(next_state) +"}"
            output_string += f";{src},{symbol},{dst}"
    print(output_string, end="\n\n")
    
    if DEBUG_F:
        new_af = read_input(output_string)
        table = make_table(new_af[4], new_af[3])
        global TESTE
        print("\n-------------\nTESTE", TESTE, "-  F")
        print_table(table)
        TESTE += 1
        

def make_table(transitions:list[tuple[str]], alphabet:set[str]) -> defaultdict[dict[str]]:
    '''
    Cria uma tabela de transições a partir da entrada.
    '''
    print(transitions)
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
        output_string += f"    {i}      "
    output_string += "\n-------------------------------------------\n"
    for state, transitions in table_set:
        src = state.ljust(6)
        output_string += src
        for sym in simbols:
            destination = transitions[sym].ljust(6)
            output_string += destination.rjust(12)
        output_string += "\n"
    print(output_string)
