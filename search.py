# accepts file with model specification
# extract constants
# add inequalities for each pair of constants
# insert that as a theory
# return the "closest existing theory"

import pandas as pd
import relationship


def extract_constants(lines):
    unique_constants = []
    for line in lines:
        if "(" in line:
            for c in range(line.index("(")+1, line.index(")")-1, 1):
                while line[c] != "," and line[c] not in unique_constants:
                    unique_constants.append(line[c])
    return unique_constants


def make_inequalities(unique_constants):
    # num_pairs = (len(unique_constants)*(len(unique_constants)-1))/2
    pairs = []

    # find all unique pairs
    for i in range(0, len(unique_constants)-1, 1):
        for j in range(i+1, len(unique_constants), 1):
            pairs.append([unique_constants[i], unique_constants[j]])
    # print(pairs)

    # create list of statements with the pairs
    statements = []
    for pair in pairs:
        s = pair[0] + "!=" + pair[1] + ".\n"
        statements.append(s)
    # print(statements)
    return statements


def find_position(chain, mod, low, high):
    if low == high:
        compare_low = relationship.consistency(mod, chain[low])
        if compare_low is True:
            return low + 1
        # take out inconclusive??
        elif compare_low is False:
            return low

    if low > high:
        return low

    mid = (low+high)//2
    compare_mid = relationship.consistency(mod, chain[mid])

    # lower half
    if compare_mid is False:
        return find_position(chain, mod, low, mid-1)
    # upper half
    elif compare_mid is True:
        return find_position(chain, mod, mid+1, high)
    # does not belong "inconclusive"
    else:
        return -1


def search(in_chain, new_t):
    location = find_position(in_chain, new_t, 0, len(in_chain)-1)
    if location != -1:
        if location < len(in_chain)-1:
            return [in_chain[location], in_chain[location+1]]
        elif location == len(in_chain)-1:
            return [in_chain(location)]
    else:
        return -1


def main(csv_file, model_file):
    chains_df = pd.read_csv(csv_file)
    chains_list = []
    [chains_list.append(row) for row in chains_df]
    chains_list = chains_df.values.tolist()

    for i, c in enumerate(chains_list):
        chains_list[i] = list(filter(lambda a: pd.notna(a), c))
    input_chains = [[str(s) + ".in" for s in c] for c in chains_list]

    for i, c in enumerate(chains_list):
        chains_list[i] = list(filter(lambda a: pd.notna(a), c))
    input_chains = [[str(s) + ".in" for s in c] for c in chains_list]

    with open(model_file, "r+") as f:
        lines = f.readlines()

        input1 = (extract_constants(lines))
        add_these_lines = make_inequalities(input1)

        for line in add_these_lines:
            f.write(line)
    f.close()

    f = open(model_file, "r")
    model_spec_lines = f.readlines()
    relationship.replace_symbol(model_spec_lines, ".\n", "")
    relationship.replace_symbol(model_spec_lines, "\t", "")

    x = []

    for i, chain in enumerate(chains_list):
        condition = relationship.consistency(model_spec_lines, chain[0] + ".in")
        if condition is not True:
            continue
        else:
            item = search(input_chains[i], model_file)
            if item != -1:
                x.extend(item)
            closest_theories = list(set(x))
            print("closest theories are: ", closest_theories)

    f.close()

    print("done")


main("anti_strict_model_spec.in")
