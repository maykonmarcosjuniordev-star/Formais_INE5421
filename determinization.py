from collections import defaultdict
from Utilis import read_input, print_output


# Determiniza um AFND sem épsilon-transições.
def determinize_without_epsilon(num_states, initial_state, final_states, alphabet, transitions):
    new_transitions = defaultdict(dict)
    new_final_states = set()
    states_queue = [(initial_state,)]

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
            next_state_tuple = tuple(sorted(next_states))
            new_transitions[state_tuple][symbol] = next_state_tuple
            if next_state_tuple not in new_transitions:
                states_queue.append(next_state_tuple)

    return new_transitions, new_final_states

# Determiniza um AFND com épsilon-transições.
def determinize_with_epsilon(num_states, initial_state, final_states, alphabet, transitions):
    new_transitions = defaultdict(dict)
    new_final_states = set()
    states_queue = [closure({initial_state}, transitions)]

    while states_queue:
        state = states_queue.pop(0)
        state_tuple = tuple(sorted(state))
        if any(s in final_states for s in state_tuple):
            new_final_states.add(state_tuple)

        for symbol in alphabet.union({"&"}):
            next_states = set()
            for s in state_tuple:
                for src, sym, dst in transitions:
                    if src == s and (sym == symbol or (sym == "&" and symbol == "&")):
                        next_states.add(dst)
            next_state_tuple = tuple(sorted(closure(next_states, transitions)))
            new_transitions[state_tuple][symbol] = next_state_tuple
            if next_state_tuple not in new_transitions:
                states_queue.append(list(next_state_tuple))

    return new_transitions, new_final_states

# Calcula o fecho épsilon transitivo de um conjunto de estados.
def closure(states, transitions):
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
    has_epsilon = any(sym == "&" for _, sym, _ in transitions)

    func = determinize_without_epsilon
    if has_epsilon:
        func = determinize_with_epsilon
    new_transitions, new_final_states = func(num_states,
                                             initial_state,
                                             final_states,
                                             alphabet,
                                             transitions)

    print_output(new_transitions, initial_state, new_final_states, alphabet)

while True:
    try:
        determinize()
    except EOFError:
        break
