from collections import defaultdict
from Utilis import read_input, print_output

DEBUG = False
TESTE = 0

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
    if DEBUG:
        global TESTE
        TESTE += 1
        print("\n----------------------------\nDeterminização", TESTE, "iniciada.", end="\n\n")
    num_states, initial_state, final_states, alphabet, transitions = read_input()
    is_epsilon = any(sym == "&" for _, sym, _ in transitions)
    alphabet.discard("&")
    new_transitions = defaultdict(dict)
    new_final_states = set()
    if is_epsilon:
        initial_state = closure({initial_state}, transitions)
    states_queue = [set(initial_state)]

    while states_queue:
        if DEBUG:
            print("states queue =", states_queue,
                  "\nnew transitions =", sorted(new_transitions.items()),
                  "\nnew final states =", new_final_states, end="\n\n")
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
