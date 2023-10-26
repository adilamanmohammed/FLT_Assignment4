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

def find_nullable_variables(grammar, non_terminals):
    nullable_variables = set()
    change = True

    while change:
        change = False
        for non_terminal in non_terminals:
            if non_terminal not in nullable_variables:
                for production in grammar.get(non_terminal, []):
                    if all(symbol in nullable_variables or symbol == 'ε' for symbol in production):
                        nullable_variables.add(non_terminal)
                        change = True
                        break
    return nullable_variables

def remove_epsilon_productions(grammar, nullable_variables):
    new_grammar = {k: [] for k in grammar}
    for non_terminal, productions in grammar.items():
        for production in productions:
            if production != ['ε']:
                new_grammar[non_terminal].append(production)
                for symbol in production:
                    if symbol in nullable_variables:
                        new_production = [s for s in production if s != symbol]
                        if new_production and new_production != production:
                            new_grammar[non_terminal].append(new_production)

    # Remove duplicate productions
    for non_terminal in new_grammar:
        new_grammar[non_terminal] = [list(t) for t in set(tuple(p) for p in new_grammar[non_terminal])]

    # Remove ε-productions from variables except for those originally nullable
    for non_terminal in list(new_grammar.keys()):
        if non_terminal not in nullable_variables and ['ε'] in new_grammar[non_terminal]:
            new_grammar[non_terminal].remove(['ε'])
        if not new_grammar[non_terminal]:
            del new_grammar[non_terminal]

    return new_grammar

def write_grammar_to_file(file_path, grammar):
    with open(file_path, 'w') as f:
        for lhs, productions in grammar.items():
            for production in productions:
                f.write(f"{lhs} ::= {' '.join(production)}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py input_file output_file")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    grammar, terminals, non_terminals = parse_grammar(input_file_path)

    nullable_variables = find_nullable_variables(grammar, non_terminals)
    epsilon_free_grammar = remove_epsilon_productions(grammar, nullable_variables)

    write_grammar_to_file(output_file_path, epsilon_free_grammar)

    print("Output written to", output_file_path)

    print("\nContents of", output_file_path + ":")
    with open(output_file_path, 'r') as f:
        print(f.read())
