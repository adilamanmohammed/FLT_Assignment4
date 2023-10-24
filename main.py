def read_cfg(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    cfg = {}
    for line in lines:
        lhs, rhs = line.strip().split("::=")
        lhs = lhs.strip()
        rhs = [r.strip() for r in rhs.split('|')]
        cfg[lhs] = rhs

    return cfg


def remove_epsilon_productions(cfg):
    nullable = set()

    change = True
    while change:
        change = False
        for lhs, rhss in cfg.items():
            for rhs in rhss:
                if all(symbol in nullable or symbol == '' for symbol in rhs.split()):
                    if lhs not in nullable:
                        nullable.add(lhs)
                        change = True

    new_cfg = {}
    for lhs, rhss in cfg.items():
        new_productions = []
        for rhs in rhss:
            symbols = rhs.split()
            new_productions.append(rhs)

            for symbol in symbols:
                if symbol in nullable:
                    new_productions.append(' '.join([s if s != symbol else '' for s in symbols]).strip())

        new_cfg[lhs] = list(set(new_productions))

    # If start symbol is nullable, introduce a new start symbol
    start_symbol = list(cfg.keys())[0]
    if start_symbol in nullable:
        new_start = start_symbol + "1"
        new_cfg[new_start] = ["", start_symbol]
    else:
        new_start = start_symbol

    return new_cfg, new_start


def remove_unproductive_symbols(cfg):
    productive = set()

    change = True
    while change:
        change = False
        for lhs, rhss in cfg.items():
            for rhs in rhss:
                if all(symbol in productive or not symbol.startswith('<') for symbol in rhs.split()):
                    if lhs not in productive:
                        productive.add(lhs)
                        change = True

    new_cfg = {}
    for lhs, rhss in cfg.items():
        if lhs in productive:
            new_rhs = [rhs for rhs in rhss if all(symbol in productive or not symbol.startswith('<') for symbol in rhs.split())]
            if new_rhs:
                new_cfg[lhs] = new_rhs

    return new_cfg


def remove_unreachable_symbols(cfg, start_symbol):
    reachable = {start_symbol}

    change = True
    while change:
        change = False
        for lhs in list(reachable):
            for rhs in cfg.get(lhs, []):
                for symbol in rhs.split():
                    if symbol.startswith('<') and symbol not in reachable:
                        reachable.add(symbol)
                        change = True

    new_cfg = {}
    for lhs in reachable:
        if lhs in cfg:
            new_cfg[lhs] = cfg[lhs]

    return new_cfg


def write_cfg(filename, cfg):
    with open(filename, 'w') as file:
        for lhs, rhss in cfg.items():
            for rhs in rhss:
                file.write(f"{lhs} ::= {rhs}\n")


def main(input_file, output_file):
    cfg = read_cfg(input_file)

    cfg, start_symbol = remove_epsilon_productions(cfg)
    cfg = remove_unproductive_symbols(cfg)
    cfg = remove_unreachable_symbols(cfg, start_symbol)

    write_cfg(output_file, cfg)


if __name__ == "__main__":
    import sys
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)
