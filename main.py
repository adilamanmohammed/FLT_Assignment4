# Define sets to store terminal and non-terminal symbols
terminal = set()
non_terminal = set()

# Read equations from the input file
with open("input.txt", "r") as file:
    equations = file.read().splitlines()

# Function to process a string and identify non-terminals
def identify_non_terminals(s):
    s = s.replace("(", " ").replace(")", " ")  # Treat "(" and ")" as spaces
    symbols = s.split()
    for symbol in symbols:
        # Check if the symbol is a non-terminal enclosed in "<" and ">"
        if symbol.startswith("<") and symbol.endswith(">"):
            non_terminal.add(symbol)  # Add the non-terminal to the set
        else:
            terminal.add(symbol)  # Add the symbol to the terminal set

# Iterate through each equation in the list of equations
for equation in equations:
    # Split the equation into lhs and rhs using "::=" as the delimiter
    lhs, rhs = equation.split("::=")
    
    # Process the lhs to identify non-terminal symbols
    identify_non_terminals(lhs)
    
    # Process the rhs to identify terminal and non-terminal strings
    identify_non_terminals(rhs)

# Now, you have populated both the terminal and non-terminal sets
print("terminals:", terminal)
print("non-terminals:", non_terminal)
