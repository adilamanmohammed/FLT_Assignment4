"""
Name : Adil Aman Mohammed
Course : Formal language theory
Assignment no: 4
CWID : A20395630
Description: the below code is an implementation of taking input CFG and applying 3 algorithms (epsilon-removal, unproductive removal, unreachable removal)
"""

import sys

#This function reads the CFG from a file and returns three sets: 
#the CFG itself, the set of terminal symbols, and the set of non-terminal symbols.

def function_parse_grammar(file_path):
    
    CFG_Grammar = {}  #the following dictionary will store the CFG
    terminals_list = set() #the following set will store all the terminal symbols.
    non_terminals_list = set()  #the following set will store all the non-terminal symbols.

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  #removing the leading and trailing whitespaces.
            if line:
                #splitting the line into the left-hand side and right-hand side of the production.
                LHS, RHS = line.split("::=")
                LHS = LHS.strip()
                #splitting the RHS into symbols and strip whitespaces from each symbol.
                RHS = tuple(symbol.strip() for symbol in RHS.split() if symbol.strip())

                non_terminals_list.add(LHS)
                for symbol in RHS:
                    if symbol.startswith("<") and symbol.endswith(">"):
                        #if the symbol is surrounded by '<>', it's a non-terminal.
                        non_terminals_list.add(symbol)
                    else:
                        # Otherwise, it's a terminal.
                        terminals_list.add(symbol)

                #Adding the production to the CFG. If LHS is already a key in CFG_Grammar,adding RHS to its value set.
                # Otherwise, create a new entry in CFG_Grammar with LHS as the key and a set containing RHS as the value.
                if LHS in CFG_Grammar:
                    CFG_Grammar[LHS].add(RHS)
                else:
                    CFG_Grammar[LHS] = {RHS}

    return CFG_Grammar, terminals_list, non_terminals_list



#the following function finds the set of nullable non-terminals in the CFG.
#A non-terminal is nullable if it can derive the empty string.

def Finding_nullable_var_set(CFG_Grammar, non_terminals_list):
    
    nullable_var_set = set()
    # initially,adding to nullable_var_set all non-terminals that have an ε-production.
    for non_terminal, productions in CFG_Grammar.items():
        if ('ε',) in productions or () in productions:
            nullable_var_set.add(non_terminal)

    #kEep iterating until no more Changes are made.
    CHANGED_FLAG = True
    while CHANGED_FLAG:
        CHANGED_FLAG = False
        for non_terminal in non_terminals_list:
            if non_terminal not in nullable_var_set:
                for production in CFG_Grammar.get(non_terminal, set()):
                    # If all symbols in a production are nullable or ε,adding the non-terminal to nullable_var_set.
                    if all(symbol in nullable_var_set or symbol == 'ε' for symbol in production):
                        nullable_var_set.add(non_terminal)
                        CHANGED_FLAG = True
                        break

    return nullable_var_set



"""
   the following functionadds new productions to the CFG to account for the nullability of non-terminals.
    For each production that contains a nullable non-terminal, new productions areaddinged for each possible way
    of omitting the nullable non-terminals.
"""
def function_add_nullable_productions(CFG_Grammar, nullable_var_set):
   
    new_CFG_Grammar = {k: {tuple(prod) for prod in v} for k, v in CFG_Grammar.items()}
    for non_terminal, productions in CFG_Grammar.items():
        for production in productions:
            if any(symbol in nullable_var_set for symbol in production):
                new_prods = [production]
                # For each nullable symbol in the production,adding new productions with the symbol omitted.
                for symbol in production:
                    if symbol in nullable_var_set:
                        new_prods = [prod[:i] + prod[i + 1:] for prod in new_prods for i in range(len(prod)) if prod[i] == symbol] + new_prods
                new_CFG_Grammar[non_terminal].update(tuple(prod) for prod in new_prods)
    return new_CFG_Grammar


#the following functionremoving thes ε-productions from the CFG.
def function_eps_remo(CFG_Grammar, non_terminals_list, start_char):

    nullable_var_set = Finding_nullable_var_set(CFG_Grammar, non_terminals_list)
    CFG_Grammar = function_add_nullable_productions(CFG_Grammar, nullable_var_set)
    new_CFG_Grammar = {k: {tuple(prod) for prod in v} for k, v in CFG_Grammar.items()}

    #removing the ε-productions from the grammar.
    for non_terminal in non_terminals_list:
        if non_terminal in new_CFG_Grammar:
            new_CFG_Grammar[non_terminal] = {production for production in new_CFG_Grammar[non_terminal] if production != ('ε',) and production != ()}

    #if the start symbol is nullable,adding a new start symbol with an ε-production and a production to the old start symbol.
    if start_char in nullable_var_set:
        new_start_char = "<" + start_char[1:-1] + "1>"
        new_CFG_Grammar[new_start_char] = {('',), (start_char,)}
        non_terminals_list.add(new_start_char)
        start_char = new_start_char

    return new_CFG_Grammar, non_terminals_list, start_char

def function_remove_unproductive(CFG_Grammar, terminals_list, non_terminals_list):
    """
   the following functionremoving thes unproductive non-terminals and productions from the CFG.
    A non-terminal is unproductive if it does not derive any string of terminal symbols.
    """
    productive_char_set = set(terminals_list)
    productive_CFG_Grammar = {}

    change = True
    while change:
        change = False
        for non_terminal in non_terminals_list:
            if non_terminal not in productive_char_set:
                for production in CFG_Grammar.get(non_terminal, set()):
                    #if all the symbols in a production are productive,adding the non-terminal to productive_char_set.
                    if all(symbol in productive_char_set for symbol in production):
                        productive_char_set.add(non_terminal)
                        change = True
                        break

    #removing the unproductive non-terminals and productions from the CFG.
    for non_terminal in non_terminals_list:
        if non_terminal in productive_char_set:
            productive_CFG_Grammar[non_terminal] = set()
            for production in CFG_Grammar.get(non_terminal, set()):
                if all(symbol in productive_char_set for symbol in production):
                    productive_CFG_Grammar[non_terminal].add(production)

    return productive_CFG_Grammar, terminals_list, productive_char_set

def function_remove_unreachable_character(CFG_Grammar, start_char):
    """
   the following functionremoving thes unreachable non-terminals and productions from the CFG.
    A non-terminal is unreachable if it cannot be derived from the start symbol.
    """
    reachable_char_set = {start_char}
    new_added_set = True
    while new_added_set:
        new_added_set = False
        for non_terminal in list(reachable_char_set):  
            if non_terminal in CFG_Grammar:
                for production in CFG_Grammar[non_terminal]:
                    for symbol in production:
                        if symbol not in reachable_char_set:
                            reachable_char_set.add(symbol)
                            new_added_set = True

    #removing the unreachable non-terminals and productions from the CFG.
    unreachable_CFG_Grammar = {k: v for k, v in CFG_Grammar.items() if k in reachable_char_set}
    for non_terminal in unreachable_CFG_Grammar:
        unreachable_CFG_Grammar[non_terminal] = {production for production in unreachable_CFG_Grammar[non_terminal] if all(symbol in reachable_char_set for symbol in production)}

    return unreachable_CFG_Grammar, reachable_char_set

if __name__ == "__main__":
    #checking if the correct number of command line arguments are provided
    if len(sys.argv) != 3:
        print("Usage error: format is: python script_name.py input_file output_file")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    CFG_Grammar, terminals_list, non_terminals_list = function_parse_grammar(input_file_path)
    start_char = next(iter(CFG_Grammar))

    #removing the unproductive non-terminals and productions.
    productive_CFG_Grammar, productive_terminals_list, productive_non_terminals_list = function_remove_unproductive(CFG_Grammar, terminals_list, non_terminals_list)
    #removing the unreachable non-terminals and productions.
    reachable_CFG_Grammar, reachable_char_set = function_remove_unreachable_character(productive_CFG_Grammar, start_char)
    #removing the ε-productions.
    final_CFG_Grammar, final_non_terminals_list, final_start_char = function_eps_remo(reachable_CFG_Grammar, reachable_char_set, start_char)

    #displaying and store the final CFG.
    with open(output_file_path, 'w') as output_file:
        for non_terminal in sorted(final_non_terminals_list):
            if non_terminal in final_CFG_Grammar:
                for production in sorted(final_CFG_Grammar[non_terminal], key=lambda x: ' '.join(x)):
                    production_str = f"{non_terminal} ::= {' '.join(production)}"
                    print(production_str)  #displaying to console
                    output_file.write(production_str + '\n')  #writting to the output file
