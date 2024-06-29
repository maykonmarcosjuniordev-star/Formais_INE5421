from collections import defaultdict
from first_follow import first, follow, get_grammar

DEBUG_LR = False
DEBUG_NF = False

def left_recursion(grammar:dict, rec_fathers:list, prods:list) -> tuple:
    if DEBUG_LR:
        print('verificando recursão à esquerda para', h, "nas produções", prods)
    has_epsilon = any([p == "&" for p in prods])
    for p in prods:
        if p == "&":
            if DEBUG_LR:
                print('-> produção anulável, continuando')
            continue
        finished = True
        for sym in p:
            finished = False
            if DEBUG_LR:
                print('-> verificando o símbolo', sym, 'na produção', p)
            if sym.islower():
                if DEBUG_LR:
                    print(f'-> {sym} é T, ignorando a produção', p)                
                break
            if sym in rec_fathers:
                print('->-> recursão à esquerda encontrada')
                return True, has_epsilon
            if DEBUG_LR:
                print(f'->-> {sym} é NT, recursão necessária')
            rec_fathers.append(sym)
            lr = left_recursion(grammar, rec_fathers, grammar[sym])
            if lr[0]:
                return True, has_epsilon
            if not lr[1]:
                break
            finished = True
            if DEBUG_LR:                
                print('->-> o símbolo', sym, 'é anulável, continuando a verificação de', p)
        if finished:
            if DEBUG_LR:
                print(f'->->-> a cabeça de {p} é na verdade anulável')
            has_epsilon = True
    return False, has_epsilon

def is_left_recursive(grammar:dict) -> bool:
    for h, prods in grammar.items():
        if left_recursion(grammar, [h], prods)[0]:
            print("gramática recursiva à esquerda")
            return True
        if DEBUG_LR:
            print(f'----------------\nrecursão à esquerda não encontrada para {h}\n----------------')
    return False


def is_not_factored(grammar: dict, firsts: dict,
                    follows: dict) -> bool:
    for left, prods in grammar.items():
        prefixes = defaultdict(set)
        if DEBUG_NF:
            print(f"Verificando fatoração para {left} nas produções {prods}")
        for prod in prods:
            if DEBUG_NF:
                print(f"-> Verificando {prod}")
            first_set = set()
            for sym in prod:
                if sym.islower() or sym == "&":
                    if DEBUG_NF:
                        print(f"->-> {sym} é terminal, adicionando ao first_set")
                    first_set.add(sym)
                    break
                if DEBUG_NF:
                    print(f"->-> {sym} é não-terminal, adicionando first[{sym}] = {firsts[sym]}")
                first_set |= firsts[sym]
                if "&" not in firsts[sym]:
                    if DEBUG_NF:
                        print(f"->-> {sym} não é anulável, parando")
                    first_set -= {"&"}
                    break
            if "&" in first_set:
                if DEBUG_NF:
                    print(f"->-> {prod} é anulável, adicionando follow[{left}] = {follows[left] - {'$'}}")
                first_set -= {"&"}
                first_set |= follows[left] - {"$"}
            if DEBUG_NF:
                print(f"->->-> first_set = {first_set}")
            for symbol in first_set:
                prefixes[symbol].add(prod)

        # Check for common prefixes
        if DEBUG_NF:
            print(f"->Factors of {left} = {dict(prefixes)}")
        if any(len(p) > 1 for p in prefixes.values()):
            print("gramática não fatorada")
            return True
    if DEBUG_NF:
        print("_______________ gramática fatorada _______________")
    return False


def print_ll1(ll1):
    terminals = sorted({symbol for key in ll1 for symbol in ll1[key]})
    non_terminals = sorted(ll1.keys())
    
    # Print header
    print("  | ", end="")
    for terminal in terminals:
        print(f"{terminal:4}", end=" ")
    print()
    print("-" * (5 + 5 * len(terminals)))
    
    # Print table content
    for non_terminal in non_terminals:
        print(f"{non_terminal} | ", end="")
        for terminal in terminals:
            if terminal in ll1[non_terminal]:
                print(f"{ll1[non_terminal][terminal]:4}", end=" ")
            else:
                print("    ", end=" ")
        print()

"""
Teste 1
 -> Input: E = TA; A = mTA; A = &; T = FB; B = vFB; B = &; F = i; F = oEc;
 -> Output: {A,B,E,F,T};E;{c,i,m,o,v,$};[A,c,3][A,m,2][A,$,3][B,c,6][B,m,6][B,v,5][B,$,6][E,i,1][E,o,1][F,i,7][F,o,8][T,i,4][T,o,4]

Teste 2
 -> Input: P = KL; P = bKLe; K = cK; K = TV; T = tT; T = &; V = vV; V = &; L = mL; L = &;
 -> Output: {K,L,P,T,V},P,{b,c,e,m,t,v,$};[K,c,3][K,e,4][K,m,4][K,t,4][K,v,4][K,$,4][L,e,10][L,m,9][L,$,10][P,b,2][P,c,1][P,m,1][P,t,1][P,v,1][P,$,1][T,e,6][T,m,6][T,t,5][T,v,6][T,$,6][V,e,8][V,m,8][V,v,7][V,$,8]

Teste 3
 -> Input: P = KVC; K = cK; K = &; V = vV; V = F; F = fPiF; F = &; C = bVCe; C = miC; C = &;
 -> Output: {C,F,K,P,V},P,{b,c,e,f,i,m,v,$};[C,b,8][C,e,10][C,i,10][C,m,9][C,$,10][F,b,7][F,e,7][F,f,6][F,i,7][F,m,7][F,$,7][K,b,3][K,c,2][K,f,3][K,i,3][K,m,3][K,v,3][K,$,3][P,b,1][P,c,1][P,f,1][P,i,1][P,m,1][P,v,1][P,$,1][V,b,5][V,e,5][V,f,5][V,i,5][V,m,5][V,v,4][V,$,5]


"""

def ll1(grammar:dict, firsts:dict, follows:dict) -> dict:
    ll1_table = defaultdict(dict)    
    for left, prods in grammar.items():
        for prod in prods:
            first_set = set()
            for sym in prod:
                if sym.islower() or sym == "&":
                    first_set.add(sym)
                    break
                first_set |= firsts[sym]
                if "&" not in firsts[sym]:
                    break
            if "&" in first_set:
                first_set -= {"&"}
                first_set |= follows[left] - {"$"}
            for terminal in first_set:
                if terminal in ll1_table[left]:
                    print(f"Conflito encontrado em {left} -> {prod}")
                    return None  # Grammar is not LL(1)
                ll1_table[left][terminal] = prod
    return ll1_table

def main():
    grammar, entry_order = get_grammar(input())
    firsts = first(grammar)
    follows = follow(grammar, firsts, entry_order)
    if is_left_recursive(grammar) or is_not_factored(grammar, firsts, follows):
        return 1
    LL1 = ll1(grammar, firsts, follows)
    print_ll1(LL1)

if __name__ == '__main__':
    while True:
        try:
            main()
            # break
            if DEBUG_LR or DEBUG_NF:
                print("\n-----------------------------\n-----------------------------\n")
        except EOFError:
            break

