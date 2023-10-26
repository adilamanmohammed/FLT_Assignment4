import sys

def parse_grammar(file_path):
    grammar = {}
    terminals = set()
    non_terminals = set()

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                lhs, rhs = line.split("::=")
                lhs = lhs.strip()
                rhs = [symbol.strip() for symbol in rhs.split() if symbol.strip()]

                non_terminals.add(lhs)
                for symbol in rhs:
                    if symbol.startswith("<") and symbol.endswith(">"):
                        non_terminals.add(symbol)
                    else:
                        terminals.add(symbol)

                if lhs in grammar:
                    grammar[lhs].append(rhs)
                else:
                    grammar[lhs] = [rhs]

    return grammar, terminals, non_terminals

def remove_unproductive(grammar, terminals, non_terminals):
    productive_grammar = {k: [] for k in grammar}
    productive_non_terminals = set()

    productive_terminals = set(terminals)

    new_marked = True
    while new_marked:
        new_marked = False
        for non_terminal, productions in grammar.items():
            if non_terminal not in productive_non_terminals:
                for production in productions:
                    if all(symbol in productive_terminals or symbol in productive_non_terminals for symbol in production):
                        productive_non_terminals.add(non_terminal)
                        new_marked = True
                        break

    for non_terminal, productions in grammar.items():
        for production in productions:
            if all(symbol in productive_terminals or symbol in productive_non_terminals for symbol in production):
                productive_grammar[non_terminal].append(production)

    for non_terminal in list(productive_grammar.keys()):
        if not productive_grammar[non_terminal]:
            del productive_grammar[non_terminal]

    return productive_grammar

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py input_file")
        sys.exit(1)

    input_file_path = sys.argv[1]
    grammar, terminals, non_terminals = parse_grammar(input_file_path)
    productive_grammar = remove_unproductive(grammar, terminals, non_terminals)

    print("Productive Grammar:")
    for lhs, productions in productive_grammar.items():
        for production in productions:
            print(f"{lhs} ::= {' '.join(production)}")
