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
        self.leaf = 0
        self.pai = None

    def __str__(self):
        return f'{self.value}' # f'''({self.left} <-- {self.value} --> {self.right}) '''


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
            if char == '&':
                leaf.nullable = True
            elif not c2:
                alphabet.append(char)
            leaves.append(leaf)
            leaf.leaf = len(leaves)
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
    print('\nregex =', "".join([str(n) for n in regex]))
    prt = [n.value for n in nodes]
    print('nodes originais =', prt)
    while i < len(nodes):
        node = nodes[i]
        if node.value == '.':
            node.left = nodes[i-1]
            node.right = nodes[i+1]
            nodes[i-1] = node
            node.left.pai = node
            node.right.pai = node
            nodes.pop(i)
            nodes.pop(i)
        else:
            i += 1
        prt = [n.value for n in nodes]
        print('nodes =', prt)
    i = 1
    print('------')
    prt = [n.value for n in nodes]
    print('nodes =', prt)
    while i < len(nodes):
        node = nodes[i]
        if node.value == '|':
            node.left = nodes[i-1]
            node.right = nodes[i+1]
            nodes[i-1] = node
            node.left.pai = node
            node.right.pai = node
            nodes.pop(i)
            nodes.pop(i)
        else:
            i += 1
        prt = [n.value for n in nodes]
        print('nodes =', prt)

    return nodes[-1]

# regex = "(&|b)(ab)*(&|a)"
# regex = 'aa*(bb*aa*b)*'
# regex = "a(a|b)*a"
# regex = "a(a*(bb*a)*)*|b(b*(aa*b)*)*"
# regex = "a(b|c(d*e))f"

# _, regex, _ = fit_regex(regex)
# out = parse_regex(regex)
# print(out)

def build_tree(regex, leaves):
    tree = parse_regex(regex)
    # Raiz é a concatenação da regex com '#'
    root = Node('.')
    root.right = Node('#')
    root.right.pai = root
    # Constrói a sub-árvore para a regex original
    root.left = tree
    tree.pai = root
    return root

def compute_firstpos(node):
    if not node:
        return set()
    
    if node.value == '*':
        return compute_firstpos(node.left)
    
    if node.value == '|':
        return compute_firstpos(node.left) | compute_firstpos(node.right)
    
    if node.value == '.':
        first_pos = compute_firstpos(node.left)
        if node.left and node.left.nullable:
            first_pos |= compute_firstpos(node.right)
        return first_pos

    if node.value == '&':
        return set()

    return {node}

def compute_lastpos(node):
    if not node:
        return set()
    
    if node.value == '*':
        last_pos = compute_lastpos(node.left)
        return last_pos
    
    if node.value == '|':
        return compute_lastpos(node.left) | compute_lastpos(node.right)
    
    if node.value == '.':
        last_pos = compute_lastpos(node.right)
        if node.right and node.right.nullable:
            last_pos |= compute_lastpos(node.left)

    if node.value == '&':
        return set()

    return {node}

def compute_followpos(node, firstpos, lastpos):
    follow_pos = defaultdict(set)
    
    for node in firstpos:
        follow_pos[node] |= compute_firstpos(node.right)
    
    for state in lastpos:
        if node.value == '*':
            follow_pos[state] |= compute_firstpos(node.left)
        else:
            follow_pos[state] |= compute_lastpos(node.right)
    
    return follow_pos

def compute_followpos(root, firstpos, lastpos):
    follow_pos = defaultdict(set)

    def visit(node):
        if not node:
            return
        if node.leaf:  # Nó folha
            if node.pai.value == '.':
                right_sibling = node.pai.right
                if right_sibling:
                    follow_pos[node] |= compute_firstpos(right_sibling)

            elif node.pai.value == '*':
                follow_pos[node] |= compute_firstpos(node.pai.left)

            elif node.pai.value == '|':
                if node is node.pai.left:
                    follow_pos[node] |= compute_firstpos(node.pai.right)
                else:
                    follow_pos[node] |= compute_firstpos(node.pai.left)

            if node in lastpos:
                if node.pai.pai:
                    visit(node.pai)

        else:  # Nó não-folha
            visit(node.left)
            visit(node.right)

    visit(root)
    return follow_pos

def build_dfa(regex):
    alphabet, new_regex, leaves = fit_regex(regex)
    tree = build_tree(new_regex, leaves)
    first_pos = compute_firstpos(tree)
    last_pos = compute_lastpos(tree)
    follow_pos = compute_followpos(tree, first_pos, last_pos)

    states = set()
    transitions = defaultdict(dict)
    
    for state in first_pos:
        states.add(state)
    
    for state in last_pos:
        states.add(state)
    
    for state in states:
        for char in follow_pos:
            if char == state.value:
                next_state = follow_pos[char]
                transitions[state][char] = frozenset(next_state)
    
    start_state = frozenset(first_pos)
    final_states = frozenset(last_pos)# {frozenset(state) for state in last_pos if '&' in state}
    
    return states, transitions, start_state, final_states


def main(regex):
    states, transitions, start_state, final_states = build_dfa(regex)

    print("Estados:")
    for state in states:
        st = state.value
        print(" ", st)

    print("\nTransições:")
    for state, transitions_from_state in transitions.items():
        for char, next_state in transitions_from_state.items():
            print(f"  {state} -- {char} --> {next_state}")

    print("\nEstado Inicial:", start_state)
    print("Estados Finais:", final_states)

RUN = True
k = 1
while RUN:
    try:
        regex = input()
        print("\n---------------------------------------\nTeste", k)
        main(regex)
        k += 1
    except EOFError:
        break
