from collections import defaultdict


# Lê a entrada no formato especificado.
def read_input():
    entry = input().split(";")
    num_states = int(entry[0])
    initial_state = entry[1]
    final_states = set(entry[2].strip("{}").split(","))
    alphabet = set(entry[3].strip("{}").split(","))
    transitions = entry[4:]
    transitions = [tuple(t.split(",")) for t in transitions]
    return num_states, initial_state, final_states, alphabet, transitions


# Imprime o AFD resultante.
def print_output(new_transitions, new_initial_state, new_final_states, alphabet):
    print(f"{len(new_transitions)};", end="")
    print(f"<{new_initial_state}>;", end="")
    final_states_matrix = ["".join(j for j in i) for i in sorted(new_final_states)]
    print("{" + ",".join(final_states_matrix) + "};", end="")
    print("{" + ",".join(sorted(alphabet)) + "};", end="")
    for state, transitions in sorted(new_transitions.items()):
        for symbol, next_state in sorted(transitions.items()):
            print(f"{','.join(state)},{symbol},{','.join(next_state)};", end="")
    print()

def minimize_dfa(num_states, initial_state, final_states, alphabet, transitions):
    """
    Minimiza um AFD usando o algoritmo de minimização por partições.
    """
    states = set(src for src, _, _ in transitions).union(dst for _, _, dst in transitions)
    non_final_states = states - final_states
    partitions = [non_final_states, final_states]

    while True:
        new_partitions = []
        for partition in partitions:
            partition_groups = defaultdict(set)
            for state in partition:
                group_key = tuple(sorted((transitions[(state, sym)] for sym in alphabet)))
                partition_groups[group_key].add(state)
            new_partitions.extend(partition_groups.values())
        if len(new_partitions) == len(partitions):
            break
        partitions = new_partitions

    new_transitions = defaultdict(dict)
    new_states = []
    state_map = {}
    for i, partition in enumerate(partitions):
        new_state = f"Q{i}"
        new_states.append(new_state)
        for state in partition:
            state_map[state] = new_state
        if initial_state in partition:
            new_initial_state = new_state
        if any(final in partition for final in final_states):
            new_final_states = new_state

    for src, sym, dst in transitions:
        new_src = state_map[src]
        new_dst = state_map[dst]
        new_transitions[new_src][sym] = new_dst

    return new_transitions, new_initial_state, {new_final_states}, alphabet

def minimize():
    num_states, initial_state, final_states, alphabet, transitions = read_input()
    new_transitions, new_initial_state, new_final_states, new_alphabet = minimize_dfa(num_states, initial_state, final_states, alphabet, transitions)
    print_output(new_transitions, new_initial_state, new_final_states, new_alphabet)

while True:
    try:
        minimize()
    except EOFError:
        break
