from collections import defaultdict
from Utilis import read_input, print_output

DEBUG = False

def remove_dead_and_unreacheable_states(initial_state:str, final_states:set[str],
                                       alphabet:set[str], transitions:list[tuple[str]]):
    src_states = set(src for src, _, _ in transitions)
    dst_states = set(dst for _, _, dst in transitions)
    states = src_states.union(dst_states)

    # first remove the unreacheable states
    reacheable_states = set()
    stack = [initial_state]
    while stack:
        state = stack.pop(0)
        reacheable_states.add(state)
        for src, sym, dst in transitions:
            if src == state and dst not in reacheable_states:
                stack.append(dst)
    unreacheable_states = states - reacheable_states
    for src, sym, dst in transitions:
        if src in unreacheable_states:
            transitions.remove((src, sym, dst))
    states = reacheable_states

    # now for the dead states
    queue = sorted(final_states)
    living_states = set()
    while queue:
        state = queue.pop(0)
        living_states.add(state)
        for src, sym, dst in transitions:
            if dst == state and src not in living_states:
                queue.append(src)
    dead_states = states - living_states
    for state in dead_states:
        states.discard(state)
        for src, sym, dst in transitions:
            if src == state or dst == state:
                transitions.remove((src, sym, dst))
    return living_states, transitions

def minimize(initial_state:str, final_states:set[str],
             alphabet:set[str], transitions:list[tuple[str]]):
    states, transitions = remove_dead_and_unreacheable_states(initial_state,
                                                              final_states,
                                                              alphabet, transitions)
    non_final_states = set(states) - set(final_states)
    equivalence_classes = [final_states, non_final_states]
    cls_queue = [final_states]
    while cls_queue:
        if DEBUG:
            print("\n\ncls_queue =", cls_queue)
        eq_cls = cls_queue.pop()
        for sym in alphabet:
            X = {src for src, s, dst in transitions if (src in states and s == sym and dst in eq_cls)}
            reachers = [i for i in equivalence_classes if X.intersection(i)]
            if DEBUG:
                print("----\nsym =", sym)
                print("X =", X)
                print("reachers =", reachers)
            for Y in reachers:
                x_and_y = X.intersection(Y)
                x_minus_y = Y - X
                if DEBUG:
                    print("---\nY =", Y)
                    print("x_and_y =", x_and_y)
                    print("x_minus_y =", x_minus_y)
                equivalence_classes.remove(Y)
                equivalence_classes.append(x_and_y)
                if x_minus_y:
                    equivalence_classes.append(x_minus_y)
                if Y in cls_queue:
                    cls_queue.remove(Y)
                    cls_queue.append(x_and_y)
                    if x_minus_y:
                        cls_queue.append(x_minus_y)
                else:
                    if x_minus_y:
                        cls_queue.append(min(x_and_y, x_minus_y))
    new_states = set()
    new_states_eq_cls_map = {}
    new_final_states = set()
    new_transitions = defaultdict(dict)
    new_alphabet = set()
    if DEBUG:
        print("equivalence classes =", equivalence_classes)
    for eq_cls in equivalence_classes:
        new_state = sorted(eq_cls)[0]
        if initial_state in eq_cls:
            new_initial_state = new_state
        if any(final in eq_cls for final in final_states):
            new_final_states.add(new_state)
        new_states.add(new_state)
        new_states_eq_cls_map[new_state] = eq_cls
    for src, sym, dst in transitions:
        for state, eq_cls in new_states_eq_cls_map.items():
            if src in eq_cls:
                src = state
            if dst in eq_cls:
                dst = state
        if src in new_states and dst in new_states:
            new_transitions[src][sym] = dst
            new_alphabet.add(sym)

    return new_transitions, new_initial_state, new_final_states, new_alphabet

def main():
    num_states, initial_state, final_states, alphabet, transitions = read_input()
    (new_transitions, new_initial_state,
     new_final_states, new_alphabet) = minimize(initial_state,
                                                final_states,
                                                alphabet,
                                                transitions)
    print_output(new_transitions, new_initial_state,
                 new_final_states, new_alphabet)
    if DEBUG:
        print("---------------------------------------------\n")

while True:
    try:
        main()
    except EOFError:
        break
