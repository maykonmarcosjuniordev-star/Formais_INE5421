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
    return num_states, initial_state, final_states, alphabet, transitions


def print_output(new_transitions: defaultdict, new_initial_state:str,
                 new_final_states:set, alphabet:set) -> None:
    '''
    Imprime o AFD resultante.
    '''
    # print(sorted(new_transitions.items()), end="\n\n")
    output_string = f"{len(new_transitions.keys())};"
    output_string += "{" + ",".join(sorted(new_initial_state)) + "};"
    final_states_matrix = [",".join(j for j in i) for i in sorted(new_final_states)]
    output_string += "{{" + "},{".join(final_states_matrix) + "}};"
    output_string += "{" + ",".join(sorted(alphabet)) + "}"
    for state, transitions in sorted(new_transitions.items()):
        for symbol, next_state in sorted(transitions.items()):
            src = "{" + ','.join(state) +"}"
            dst = "{" + ','.join(next_state) +"}"
            output_string += f";\n{src},{symbol},{dst}"
    print(output_string, end="\n\n")

# Calcula o fecho épsilon transitivo de um conjunto de estados.
def closure(states, transitions: list[tuple[str]]) -> set[str]:
    closure_set = set(states)
    queue = list(states)
    while queue:
        state = queue.pop(0)
        for src, sym, dst in transitions:
            if src == state and sym == "&":
                if dst not in closure_set:
                    closure_set.add(dst)
                    queue.append(dst)
    return closure_set

def determinize():
    num_states, initial_state, final_states, alphabet, transitions = read_input()
    is_epsilon = any(sym == "&" for _, sym, _ in transitions)
    alphabet.discard("&")
    new_transitions = defaultdict(dict)
    new_final_states = set()
    if is_epsilon:
        initial_state = closure({initial_state}, transitions)
    states_queue = [set(initial_state)]

    while states_queue:
        state = states_queue.pop(0)
        state_tuple = tuple(sorted(state))
        if any(s in final_states for s in state_tuple):
            new_final_states.add(state_tuple)

        for symbol in alphabet:
            next_states = set()
            for s in state_tuple:
                for src, sym, dst in transitions:
                    if src == s and sym == symbol:
                        next_states.add(dst)
            n_states = next_states
            if is_epsilon:
                n_states = closure(next_states, transitions)
            if not n_states:
                continue
            next_state_tuple = tuple(sorted(n_states))
            new_transitions[state_tuple][symbol] = next_state_tuple
            if next_state_tuple not in new_transitions:
                states_queue.append(set(next_state_tuple))
    print_output(new_transitions, initial_state, new_final_states, alphabet)

while True:
    try:
        determinize()
    except EOFError:
        break
