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
                rhs = tuple(symbol.strip() for symbol in rhs.split() if symbol.strip())

                non_terminals.add(lhs)
                for symbol in rhs:
                    if symbol.startswith("<") and symbol.endswith(">"):
                        non_terminals.add(symbol)
                    else:
                        terminals.add(symbol)

                if lhs in grammar:
                    grammar[lhs].add(rhs)
                else:
                    grammar[lhs] = {rhs}

    return grammar, terminals, non_terminals

def find_nullable_variables(grammar, non_terminals):
    nullable_variables = set()

    for non_terminal, productions in grammar.items():
        if ('ε',) in productions:
            nullable_variables.add(non_terminal)

    changed = True
    while changed:
        changed = False
        for non_terminal in non_terminals:
            if non_terminal not in nullable_variables:
                for production in grammar.get(non_terminal, set()):
                    if all(symbol in nullable_variables or symbol == 'ε' for symbol in production):
                        nullable_variables.add(non_terminal)
                        changed = True
                        break

    return nullable_variables

def add_nullable_productions(grammar, nullable_variables):
    new_grammar = {k: {tuple(prod) for prod in v} for k, v in grammar.items()}
    for non_terminal, productions in grammar.items():
        for production in productions:
            if any(symbol in nullable_variables for symbol in production):
                new_prods = [production]
                for symbol in production:
                    if symbol in nullable_variables:
                        new_prods = [prod[:i] + prod[i + 1:] for prod in new_prods for i in range(len(prod)) if prod[i] == symbol] + new_prods
                new_grammar[non_terminal].update(tuple(prod) for prod in new_prods)
    return new_grammar

def remove_eps(grammar, non_terminals):
    nullable_variables = find_nullable_variables(grammar, non_terminals)
    grammar = add_nullable_productions(grammar, nullable_variables)
    new_grammar = {k: {tuple(prod) for prod in v} for k, v in grammar.items()}

    for non_terminal in non_terminals:
        if non_terminal in new_grammar:
            new_grammar[non_terminal] = {production for production in new_grammar[non_terminal] if production != ('ε',)}
    
    return new_grammar, non_terminals

def remove_unproductive(grammar, terminals, non_terminals):
    productive_symbols = set(terminals)
    productive_grammar = {}
    
    change = True
    while change:
        change = False
        for non_terminal in non_terminals:
            if non_terminal not in productive_symbols:
                for production in grammar.get(non_terminal, set()):
                    if all(symbol in productive_symbols for symbol in production):
                        productive_symbols.add(non_terminal)
                        change = True
                        break
    
    for non_terminal in non_terminals:
        if non_terminal in productive_symbols:
            productive_grammar[non_terminal] = set()
            for production in grammar.get(non_terminal, set()):
                if all(symbol in productive_symbols for symbol in production):
                    productive_grammar[non_terminal].add(production)

    return productive_grammar, terminals, productive_symbols

def remove_unreachable_symbols(grammar, start_symbol):
    reachable_symbols = {start_symbol}
    new_added = True
    while new_added:
        new_added = False
        for non_terminal in list(reachable_symbols):  
            if non_terminal in grammar:
                for production in grammar[non_terminal]:
                    for symbol in production:
                        if symbol not in reachable_symbols:
                            reachable_symbols.add(symbol)
                            new_added = True

    unreachable_grammar = {k: v for k, v in grammar.items() if k in reachable_symbols}
    for non_terminal in unreachable_grammar:
        unreachable_grammar[non_terminal] = {production for production in unreachable_grammar[non_terminal] if all(symbol in reachable_symbols for symbol in production)}

    return unreachable_grammar, reachable_symbols

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py input_file output_file")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    grammar, terminals, non_terminals = parse_grammar(input_file_path)
    start_symbol = next(iter(grammar))

    productive_grammar, productive_terminals, productive_non_terminals = remove_unproductive(grammar, terminals, non_terminals)
    reachable_grammar, reachable_symbols = remove_unreachable_symbols(productive_grammar, start_symbol)
    final_grammar, final_non_terminals = remove_eps(reachable_grammar, reachable_symbols)

    with open(output_file_path, 'w') as f:
        for lhs, productions in sorted(final_grammar.items()):
            for production in sorted(productions):
                f.write(f"{lhs} ::= {' '.join(production)}\n")

    print("Output written to", output_file_path)

    print("\nContents of", output_file_path + ":")
    with open(output_file_path, 'r') as f:
        print(f.read())
