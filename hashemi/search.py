import pandas as pd
from relationship import parser, relationship
import os


def extract_constants(lines):
    unique_constants = []
    for line in lines:
        if "(" in line:
            for c in range(line.index("(")+1, line.index(")")-1, 1):
                while line[c] != "," and line[c] not in unique_constants:
                    unique_constants.append(line[c])
    return unique_constants


def make_inequalities(unique_constants):
    pairs = []

    # find all unique pairs
    for i in range(0, len(unique_constants)-1, 1):
        for j in range(i+1, len(unique_constants), 1):
            pairs.append([unique_constants[i], unique_constants[j]])

    # create list of inequality statements with the pairs
    statements = []
    for pair in pairs:
        s = "\n" + pair[0] + "!=" + pair[1] + ".\n"
        statements.append(s)
    return statements


def model_setup(file_name):
    with open(file_name, "r+") as f:
        lines = f.readlines()
        input1 = (extract_constants(lines))
        add_these_lines = make_inequalities(input1)
        for line in add_these_lines:
            f.write(line)
    f.close()

    with open(file_name, "r") as f:
        model_spec_lines = f.readlines()
        # remove comments
        for x, line in enumerate(model_spec_lines):
            while "%" in model_spec_lines[x]:
                model_spec_lines.remove(model_spec_lines[x])
        try:
            while True:
                model_spec_lines.remove("\n")
        except ValueError:
            pass
        relationship.parser.replace_symbol(model_spec_lines, ".\n", "")
        parser.replace_symbol(model_spec_lines, "\t", "")
    f.close()
    return model_spec_lines


# returns greatest position # of consistent theory
def find_position(chain, model_lines, low, high):
    if low == high:
        low_lines = parser.theory_setup(chain[low])
        compare_low = relationship.consistency(model_lines, low_lines)
        if compare_low is True:
            print("consistent with ", chain[low])
            return low
        elif compare_low is False:
            print("inconsistent with ", chain[low])
            # the return value will be -1 if it is inconsistent with the first theory
            return low - 1

    if low > high:
        return low

    mid = (low+high)//2
    mid_lines = parser.theory_setup(chain[mid])
    compare_mid = relationship.consistency(model_lines, mid_lines)

    # lower half
    if compare_mid is False:
        print("inconsistent with ", chain[mid])
        return find_position(chain, model_lines, low, mid-1)
    # upper half
    elif compare_mid is True:
        print("consistent with ", chain[mid])
        return find_position(chain, model_lines, mid+1, high)
    # does not belong "inconclusive"
    else:
        print("inconclusive")
        return -1


def search(in_chain, model_lines):
    location = find_position(in_chain, model_lines, 0, len(in_chain)-1)
    if location != -1:
        print("chain: ", in_chain)

        if location < len(in_chain)-1:
            return [in_chain[location], in_chain[location+1]]
        elif location == len(in_chain)-1:
            return [in_chain[location]]
    else:
        return -1


def find_theories(csv_file, model_file):
    # get the chain decomposition
    chains_df = pd.read_csv(csv_file)
    chains_list = []
    [chains_list.append(row) for row in chains_df]
    chains_list = chains_df.values.tolist()

    for i, c in enumerate(chains_list):
        chains_list[i] = list(filter(lambda a: pd.notna(a), c))
    input_chains = [[str(s) + ".in" for s in c] for c in chains_list]

    model_spec_lines = model_setup(model_file)

    closest_theories = set()
    for i, chain in enumerate(chains_list):
        theory_lines = parser.theory_setup(chain[0] + ".in")
        condition = relationship.consistency(model_spec_lines, theory_lines)
        if condition is not True:
            continue
        else:
            item = search(input_chains[i], model_spec_lines)
            if item != -1:
                closest_theories.update(item)
            print("closest theories are: ", closest_theories)

    # print
    return closest_theories


# need to loop through several models (examples + counterexamples)
def main(csv_file, path=None):

    # complete set of closest theories for every example provided
    complete_set_theories = set()

    # examples - finding all theories that are consistent with them
    for ex_file in os.listdir(path):
        # takes files specified as examples using suffix _ex.in
        if ex_file.endswith("_ex.in"):
            # find closest theories for each individual example, add to complete set
            complete_set_theories.update(find_theories(csv_file, path + "/" + ex_file))

    # counterexamples - making sure all theories found so far are inconsistent with them
    for counter_ex_file in os.listdir(path):
        # takes files specified as counterexamples using suffix _cex.in
        if counter_ex_file.endswith("_cex.in"):
            model_spec_lines = model_setup(path + "/" + counter_ex_file)
            for t in complete_set_theories:
                theory_lines = parser.theory_setup(t)

                print(t, ":", theory_lines)
                condition = relationship.consistency(model_spec_lines, theory_lines)
                # found a theory that is consistent with the counterexample. remove the theory
                if condition:
                    complete_set_theories.remove(t)


main("../semilinear-orderings.csv", path="hashemi-data")
