"""
Padrão da entrada

<número de estados>;<estado inicial>;{<estados finais>};{<alfabeto>};<transições>

Os estados são sempre identificados com letras maiúsculas.
As transições são da forma <estado origem>,<simbolo do alfabeto>,<estado destino>.
"""

from collections import defaultdict
DEBUG_S = False
DEBUG_F = False

def read_input(entry=None):
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
        table = make_table(transitions, alphabet)
        print_table(table)
    return num_states, initial_state, final_states, alphabet, transitions


def print_output(new_transitions: defaultdict, new_initial_state:str,
                 new_final_states:set, alphabet:set):
    '''
    Imprime o AFD resultante.
    '''
    output_string = f"{len(new_transitions)};"
    output_string += f"<{new_initial_state}>;"
    final_states_matrix = ["".join(j for j in i) for i in sorted(new_final_states)]
    output_string += "{" + ",".join(final_states_matrix) + "};"
    output_string += "{" + ",".join(sorted(alphabet)) + "}"
    for state, transitions in sorted(new_transitions.items()):
        for symbol, next_state in sorted(transitions.items()):
            output_string += f";{','.join(state)},{symbol},{','.join(next_state)}"
    print(output_string, end="\n\n")
    if DEBUG_F:
        new_af = read_input(output_string)
        table = make_table(new_af[4], new_af[3])
        print_table(table)


def make_table(transitions:list[tuple[str]], alphabet:set[str]):
    '''
    Cria uma tabela de transições a partir da entrada.
    '''
    # print(transitions, alphabet)
    src_states = set(i[0] for i in transitions)
    dst_states = set(",".join(i[2:]) for i in transitions)
    states = src_states.union(dst_states)
    table = defaultdict(dict)
    print(transitions)
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
    simbols = table_set[0][1].keys()
    for i in simbols:
        output_string += f"    {i}    "
    output_string += "\n----------------------------------\n"
    for state, transitions in table_set:
        output_string += f"    {state}    "
        for sym in simbols:
            destination = transitions[sym].ljust(5)
            output_string += f"    {destination}"
        output_string += "\n"
    print(output_string)
