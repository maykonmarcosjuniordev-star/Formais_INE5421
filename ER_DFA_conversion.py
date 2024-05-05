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
            leaves.append(leaf)
            leaf.leaf = len(leaves)
            leaf.firstpos.add(leaf.leaf)
            leaf.lastpos.add(leaf.leaf)
            if char == '&':
                leaf.nullable = True
                leaf.firstpos = set()
                leaf.lastpos = set()
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
    leaves.append(end)
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

def build_dfa(regex):
    alphabet, new_regex, leaves = fit_regex(regex)
    tree = build_tree(new_regex, leaves)
    compute_firstpos(tree)
    compute_lastpos(tree)
    follow_pos = defaultdict(set)
    for leaf in leaves:
        compute_followpos(leaf)
        follow_pos[leaf.leaf] = leaf.followpos
    end = tree.left

    transitions = defaultdict(dict)
    states = tree.firstpos.copy() | tree.lastpos.copy()
    
    for state in states:
        char = leaves[state-1].value
        for leaf in leaves:
            char2 = leaves[leaf.leaf-1].value
            if char == char2:
                next_state = leaf.followpos.copy()
                transitions[state][char] = (next_state)
    
    start_state = tree.firstpos
    final_states = tree.lastpos
    
    return states, transitions, start_state, final_states


def main(regex):
    # build_dfa(regex)
    states, transitions, start_state, final_states = build_dfa(regex)

    print("Estados:")
    for state in states:
        print(" ", state)

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
        print('Regex:', regex)
        main(regex)
        k += 1
        RUN = False
    except EOFError:
        break
