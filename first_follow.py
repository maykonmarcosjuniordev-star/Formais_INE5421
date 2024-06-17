"""
Os conjuntos First e Follow são necessários para a implementação do analisador sintático Preditivo LL(1).
Eles recebem uma Gramática fatorada e não recursiva à esquerda e retornam os conjuntos em ordem alfabética, com a palavra vazia (&) e o símbolo de final de sentença ($) sendo os últimos elementos do conjunto.
Cada letra minúscula é um terminal, então letras minúscula em sequência são dois terminais em sequência.
"""

from collections import defaultdict

DEBUG_FIRST = False
DEBUG_FOLLOW = False

def get_grammar(input_:str):
    entrada = input_.strip().split(";")[:-1]
    entrada = [p.strip().split(" = ") for p in entrada]
    grammar = defaultdict(list)
    T_entry_order = []
    for left, right in entrada:
        grammar[left].append(right)
        if left not in T_entry_order:
            T_entry_order.append(left)
    return grammar, T_entry_order


def print_firsts_and_follows(firsts:dict,
                             entry_order:list,
                             follows:dict) -> None:
    if DEBUG_FOLLOW or DEBUG_FIRST:
        print("\n")
    out_firsts = defaultdict(list)
    for left in entry_order:
        out_firsts[left] = sorted(firsts[left])
        if "&" in out_firsts[left]:
            out_firsts[left].remove("&")
            out_firsts[left].append("&")
    for left in entry_order:
        string = "{" + ", ".join(out_firsts[left]) + "};"
        print(f" First({left}) = {string}", end="")
    if DEBUG_FOLLOW:
        print("\n")
    out_follows = defaultdict(list)
    for left in entry_order:
        out_follows[left] = sorted(follows[left])
        if "$" in out_follows[left] and left != entry_order[0]:
            out_follows[left].remove("$")
            out_follows[left].append("$")
    for left in entry_order:
        string = "{" + ", ".join(out_follows[left]) + "};"
        print(f" Follow({left}) = {string}", end="")
    print()


def recur_first(grammar:dict, left:str, firsts:dict) -> set:
    for prod in grammar[left]:
        if DEBUG_FIRST:
            print("---\ndefinindo", left, prod, "para o firsts:")
            print("->", firsts)
        if prod[0] == "&" or prod[0].islower():
            if DEBUG_FIRST:
                print("--> adicionado", prod[0])
            firsts[left].add(prod[0])
        else:
            if DEBUG_FIRST:
                print("Recursão necessária")
            prod_first = set()
            for i, sym in enumerate(prod):
                if sym == left:
                    if DEBUG_FIRST:
                        print("-> skipping", sym)
                    continue
                elif not sym.islower():
                    sym_first = recur_first(grammar, sym, firsts)
                    prod_first = prod_first.union(sym_first)
                    if not ("&" in sym_first):
                        prod_first.discard("&")
                        break
                else:
                    prod_first.add(sym)
                    prod_first.discard("&")
                    break
            if DEBUG_FIRST:
                print("-->Recursão retornou", prod_first)
            firsts[left] = firsts[left].union(prod_first)
        if DEBUG_FIRST:
            print("definido", left, prod, "ficou:")
            print("->", firsts)
    return firsts[left]


def first(grammar:dict) -> dict:
    firsts = defaultdict(set)
    for left, right in grammar.items():
        if firsts[left]:
            if DEBUG_FIRST:
                print("-----------\nSkipping", left, right)
            continue
        if DEBUG_FIRST:
            print("-----------\nStarting with", left, right)
        firsts[left] = recur_first(grammar, left, firsts)
    return firsts


def recur_follow(must_update:dict,
                 sym:str, follows:dict) -> set:
    if not must_update[sym]:
        return
    if DEBUG_FOLLOW:
        print(f"->->->-> Updating {must_update[sym]} with FOLLOW[{sym}] =",
              follows[sym])
    dependencys = [i for i in must_update[sym] if i != sym]
    for d in dependencys:
        if DEBUG_FOLLOW:
            print(f"->->->->-> Updating {d} with ", follows[sym] - follows[d])
        follows[d] = follows[d].union(follows[sym])
        recur_follow(must_update, d, follows)



def follow(grammar:dict,
           firsts:dict,
           entry_order:list) -> dict:
    follows = defaultdict(set)
    must_update = defaultdict(set)
    follows[entry_order[0]].add("$")
    for left in entry_order:
        for prod in grammar[left]:
            for i, sym in enumerate(prod):
                if sym.islower() or sym == "&":
                    continue
                if DEBUG_FOLLOW:
                    print("-------------\n-------------\nSearching for", sym, "in",
                        prod, "from", left)
                if i == len(prod) - 1:
                    if DEBUG_FOLLOW:
                        print("-> Last symbol,", f"adding FOLLOW[{left}] =", follows[left], "to", sym)
                    if left == sym:
                        continue
                    follows[sym] = follows[sym].union(follows[left])
                    must_update[left].add(sym)
                    recur_follow(must_update, sym, follows)
                elif (i == 0) and (sym == left):
                    if DEBUG_FOLLOW:
                        print("-> Left recursive, skipping")
                    continue
                else:
                    if DEBUG_FOLLOW:
                        print("-> Verifying symbols after", sym, "in", prod)
                    for j in range(i + 1, len(prod)):
                        n_sym = prod[j]
                        if DEBUG_FOLLOW:
                            print("->-> Checking", n_sym)
                        if n_sym.islower():
                            if DEBUG_FOLLOW:
                                print("->->-> Is a terminal, adding", n_sym, "to", sym)
                            follows[sym].add(n_sym)
                            follows[sym].discard("&")
                            recur_follow(must_update, sym, follows)
                            break
                        if DEBUG_FOLLOW:
                            print(f"->->-> adding FIRST[{n_sym}] =", firsts[n_sym], "to", sym)
                        follows[sym] = follows[sym].union(firsts[n_sym])
                    if "&" in follows[sym]:
                        if DEBUG_FOLLOW:
                            print(f"-> Symbols after {sym} in {prod} are nullable,",
                                f"\n-> adding FOLLOW[{left}] =", follows[left], "to", sym)
                        follows[sym] = follows[sym].union(follows[left])
                        must_update[left].add(sym)
                if DEBUG_FOLLOW:
                    print("-------------\nFOLLOWS became\n->", [[k, f] for k, f in follows.items()])
    [o.discard("&") for o in follows.values()]
    return follows


if __name__ == '__main__':
    running = True
    while running:
        try:
            grammar, entry_order = get_grammar(input())
            ILR = any(any(b[0] == h for b in prods) for h, prods in grammar.items())
            print("gramática recursiva à esquerda\n" if ILR else "", end="")
            factors = dict(defaultdict(list))
            for h, prods in grammar.items():
                factors[h] = defaultdict(list)
                for p in prods:
                    factors[h][p[0]].append(p)
            INF = any(any(len(p) > 1 for p in prods.values()) for prods in factors.values())
            print("gramática não fatorada\n" if INF else "", end="")
            firsts = first(grammar)
            follows = follow(grammar, firsts, entry_order)
            print_firsts_and_follows(firsts, entry_order, follows)

            # running = False
        except EOFError:
            break

"""
Input 1:
-> P = KVC; K = cK; K = &; V = vV; V = F; F = fPiF; F = &; C = bVCe; C = miC; C = &;
Output 1:
-> First(P) = {b, c, f, m, v, &}; First(K) = {c, &}; First(V) = {f, v, &};
First(F) = {f, &}; First(C) = {b, m, &};
-> Follow(P) = {$, i}; Follow(K) = {b, f, i, m, v, $}; Follow(V) = {b, e, i, m, $};
Follow(F) = {b, e, i, m, $}; Follow(C) = {e, i, $};
-----------
Input 2:
-> P = KL; P = bKLe; K = cK; K = TV; T = tT; T = &; V = vV; V = &; L = mL; L = &;
Output 2:
-> First(P) = {b, c, m, t, v, &}; First(K) = {c, t, v, &};
First(T) = {t, &}; First(V) = {v, &}; First(L) = {m, &};
-> Follow(P) = {$}; Follow(K) = {e, m, $}; Follow(T) = {e, m, v, $}; 
Follow(V) = {e, m, $}; Follow(L) = {e, $};
"""    
