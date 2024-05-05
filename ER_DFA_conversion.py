"""
Implemente um programa que recebe uma Expressão Regular, Constrói a árvore da expressão e excuta a conversão para Autômato Determinístico (baseado nos cálculos de FirstPos, LastPos, e FollowPos, conforme visto em sala.

O Código deve ser feito em python3.

Padrão da entrada: Expressão Regular contendo símbolos do alfabeto e os operadores fecho (*), ou ( | ), e concat (.). O operador concat deve ser omitido, ou seja, ao invés de  "a.(a|b)*.a " a ER deve ser "a(a|b)*a".
"""

from collections import defaultdict

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
        self.nullable = False
        self.leaf = None
        self.pai = None
        self.firstpos = set()
        self.lastpos = set()
        self.followpos = set()

    def __str__(self):
        return f'{self.value}' # f'''({self.left} <-- {self.value} --> {self.right}) '''

    def __eq__(self, other):
        return str(self) == str(other)


def fit_regex(regex):
    alphabet = []
    operators = ['|', '*', '(', ')']
    non_concat_r = ['|', '(']
    non_concat_l = ['|', '*', ')']
    fitted_regex = []
    prev_char = '|'
    leaves = []

    for char in regex:
        c1 = char in operators
        c2 = char in alphabet
        c3 = char in non_concat_l
        c4 = prev_char in non_concat_r
        if not c3 and not c4:
            fitted_regex.append('.')
        fitted_regex.append(char)
        if not c1:
            leaf = Node(char)
            leaves.append((leaf, char))
            leaf.leaf = len(leaves)
            leaf.firstpos.add(leaf.leaf)
            leaf.lastpos.add(leaf.leaf)
            if char == '&':
                leaf.nullable = True
                leaf.firstpos = set()
                leaf.lastpos = set()
                leaves.pop()
            elif not c2:
                alphabet.append(char)
            fitted_regex[-1] = leaf
        prev_char = char
    return alphabet, fitted_regex, leaves


def parse_regex(regex):
    nodes = []
    i = 0
    while i < len(regex):
        char = regex[i]
        if type(char) == Node:
            nodes.append(char)
        elif char == '(':
            j = i + 1
            paren_count = 1
            while paren_count > 0:
                if regex[j] == '(':
                    paren_count += 1
                elif regex[j] == ')':
                    paren_count -= 1
                j += 1
            sub_regex = regex[i+1:j-1]
            sub_nodes = parse_regex(sub_regex, )
            nodes.append(sub_nodes)
            i = j - 1
        elif char == '*':
            prev = nodes[-1]
            node = Node(char, left=prev)
            node.nullable = True
            prev.pai = node
            nodes[-1] = node
        else:
            nodes.append(Node(char))
        i += 1
    i = 1
    while i < len(nodes):
        node = nodes[i]
        if node.value == '.':
            node.left = nodes[i-1]
            node.right = nodes[i+1]
            nodes[i-1] = node
            node.left.pai = node
            node.right.pai = node
            node.nullable = node.left.nullable and node.right.nullable
            nodes.pop(i)
            nodes.pop(i)
        else:
            i += 1
    i = 1
    while i < len(nodes):
        node = nodes[i]
        if node.value == '|':
            node.left = nodes[i-1]
            node.right = nodes[i+1]
            nodes[i-1] = node
            node.left.pai = node
            node.right.pai = node
            node.nullable = node.left.nullable or node.right.nullable
            nodes.pop(i)
            nodes.pop(i)
        else:
            i += 1

    return nodes[-1]

def build_tree(regex, leaves):
    tree = parse_regex(regex)
    # Raiz é a concatenação da regex com '#'
    end = Node('#')
    leaves.append((end, '#'))
    end.leaf = len(leaves)
    end.firstpos.add(end.leaf)
    end.lastpos.add(end.leaf)
    # Constrói a sub-árvore para a regex original
    root = Node('.')
    end.pai = root
    root.right = end
    root.left = tree
    tree.pai = root
    return root

def compute_firstpos(node:Node):
    if not node:
        return set()
    
    compute_firstpos(node.left)
    compute_firstpos(node.right)
    
    if node.value == '*':
        node.firstpos = node.left.firstpos.copy()
    
    elif node.value == '|':
        node.firstpos = node.left.firstpos.copy() | node.right.firstpos.copy()
    
    elif node.value == '.':
        node.firstpos = node.left.firstpos.copy()
        if node.left.nullable:
            node.firstpos |= node.right.firstpos.copy()

def compute_lastpos(node:Node):
    if not node:
        return set()
    
    compute_lastpos(node.left)
    compute_lastpos(node.right)

    if node.value == '*':
        node.lastpos = node.left.lastpos.copy()
    
    elif node.value == '|':
        node.lastpos = node.left.lastpos.copy() | node.right.lastpos.copy()
    
    elif node.value == '.':
        node.lastpos = node.right.lastpos.copy()
        if node.right.nullable:
            node.lastpos |= node.left.lastpos.copy()

def compute_followpos(node:Node):
    if not node or not node.pai:
        return
    if node.pai.value == '.':
        if node is node.pai.left:
            node.followpos |= node.pai.right.firstpos.copy()
            if node.pai.right.nullable:
                compute_followpos(node.pai)
                node.followpos |= node.pai.followpos.copy()
        else:
            compute_followpos(node.pai)
            node.followpos |= node.pai.followpos.copy()
    elif node.pai.value == '*':
        node.followpos |= node.firstpos.copy()
        compute_followpos(node.pai)
        node.followpos |= node.pai.followpos.copy()
    elif node.pai.value == '|':
        compute_followpos(node.pai)
        node.followpos |= node.pai.followpos.copy()

'''
Construa o autômato D-States o conjunto de estados do AFD D e D-Tran a função de transição para D, como segue:
Inicialize o autômato apenas com o estado firstpos(n0) (não marcado), onde n0 é a raiz da árvore sintática para (r)#
Para cada estado não marcado S em D-States
 - marque S
 - para cada símbolo SYM no alfabeto
    - U = {}
    - para cada p in S[SYM]
        - U = união(U, followpos(p))
    - se U não estiver em D-States	
        - Adicione U em D-State como um estado não marcado
    - D-Tran[S][SYM] = U
'''

def build_dfa(regex):
    alphabet, new_regex, leaves = fit_regex(regex)
    tree = build_tree(new_regex, leaves)
    compute_firstpos(tree)
    compute_lastpos(tree)
    follow_pos = defaultdict(set)
    leaves_by_sym = defaultdict(list)
    for leaf, char in leaves:
        compute_followpos(leaf)
        follow_pos[leaf.leaf] = leaf.followpos
        leaves_by_sym[char].append(leaf.leaf)

    
    Dstates = []
    Dtran = defaultdict(dict)
    start_state = tuple(sorted(list(tree.firstpos)))
    # s for s in Dstates if leaves[-1][0].leaf in s]
    final_states = set()
    Dstates.append(start_state)
    for state in Dstates:
        if leaves[-1][0].leaf in state:
            final_states.add(state)
        for char in alphabet:
            U = set()
            for p in leaves_by_sym[char]:
                if p in state:
                    U |= follow_pos[p]
            U = tuple(sorted(list(U)))
            if U:
                if U not in Dstates:
                    Dstates.append(U)
                Dtran[state][char] = U
    
    return Dstates, Dtran, start_state, final_states, alphabet

def print_output(new_transitions: defaultdict, new_initial_state:str,
                 new_final_states:set, alphabet:set) -> None:
    '''
    Imprime o AFD resultante.
    '''
    # print(sorted(new_transitions.items()), end="\n\n")
    output_string = f"{len(new_transitions.keys())};"
    start_state = '{' + ",".join(map(str, new_initial_state)) + '};'
    output_string += start_state
    final_states = set(['{' + ",".join(map(str, state)) + '}' for state in new_final_states])
    final_states_matrix = ["".join(j for j in i) for i in sorted(final_states)]
    output_string += "{" + ",".join(final_states_matrix) + "};"
    output_string += "{" + ",".join(sorted(list(alphabet))) + "}"
    new_transitions = {",".join(map(str, state)): {char: ",".join(map(str, next_state)) for char, next_state in sorted(new_transitions[state].items())} for state in sorted(new_transitions)}
    for state, transitions in sorted(new_transitions.items()):
        for symbol, next_state in sorted(transitions.items()):
            src = "{" + ''.join(state) +"}"
            dst = "{" + ''.join(next_state) +"}"
            output_string += f";{src},{symbol},{dst}"
    print(output_string)

def main(regex):
    # build_dfa(regex)
    states, transitions, start_state, final_states, alphabet = build_dfa(regex)

    print_output(transitions, start_state, final_states, alphabet)
    '''print("Estados:")
    for state in states:
        state = ",".join(map(str, state))
        print(f'  {{{state}}}')

    print("\nTransições:")
    for state, transitions_from_state in transitions.items():
        state = ",".join(map(str, state))
        for char, next_state in transitions_from_state.items():
            next_state = ",".join(map(str, next_state))
            print(f"  {{{state}}} -- {char} --> {{{next_state}}}")

    print(f"\nEstado Inicial: {{{','.join(map(str, start_state))}}}")
    final_states = [f'{{{",".join(map(str, state))}}}' for state in final_states]
    final_states = ",".join(final_states)
    print("Estados Finais:", final_states)'''

RUN = True
k = 1
while True:
    try:
        regex = input().strip()
        # print("\n---------------------------------------\nTeste", k, "- Regex:", regex)
        main(regex)
        # k += 1
    except EOFError:
        break
