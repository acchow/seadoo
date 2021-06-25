import pandas as pd
from p9_tools import config
from p9_tools.relationship import relationship
from p9_tools.parse import theory, model
import os

FILE_PATH = config.path
EX_PATH = config.examples
CEX_PATH = config.counterexamples
CSV_FILE = config.csv


# find the strongest theory in the chain that is consistent with the example
def find_strong(chain, model_lines):
    i = len(chain)-1    # starting index from the end
    consistent = False
    strongest = -1       # index of strongest consistent theory

    while i >= 0 and not consistent:
        theory_lines = theory.theory_setup(os.path.join(FILE_PATH, chain[i]))
        if theory_lines:
            consistent = relationship.consistency(model_lines, theory_lines,new_dir="")
            # found maximal consistent theory
            if consistent:
                print("consistent with ", chain[i])
                strongest = i
                break
            else:
                print("inconsistent with ", chain[i])
        i -= 1
    return strongest


# find weakest theory that is not consistent with the counterexample
def find_weak(chain, model_lines):
    i = 0
    max_index = len(chain)-1
    consistent = True
    weakest = len(chain)

    while i <= max_index and consistent:
        theory_lines = theory.theory_setup(os.path.join(FILE_PATH, chain[i]))
        if theory_lines:
            consistent = relationship.consistency(model_lines, theory_lines, new_dir="")
            # found minimal inconsistent theory
            if not consistent:
                print("consistent with ", chain[i])
                weakest = i
                break
            else:
                print("inconsistent with ", chain[i])
        i += 1

    return weakest


def find_bracket(chain):
    strong = len(chain)-1       # maximum index for strongest theory for examples
    weak = 0                    # minimum index for weakest theory for counterexamples

    # find strongest theory that is consistent with all examples
    for ex_file in os.listdir(EX_PATH):
        if ex_file.endswith(".in"):
            print("ex", ex_file)
            s = find_strong(chain, model.model_setup(os.path.join(EX_PATH, ex_file)))
            # update the maximum
            if s < strong:
                strong = s
                # the example is inconsistent with all theories in the chain
                if strong == -1:
                    break

    # find weakest theory that is not consistent with all counterexamples
    for cex_file in os.listdir(CEX_PATH):
        if cex_file.endswith(".in"):
            print("cex", cex_file)
            w = find_weak(chain, model.model_setup(os.path.join(CEX_PATH, cex_file)))
            # update the minimum
            if w > weak:
                weak = w
                # the counterexample is consistent with all theories in the chain
                if weak == len(chain):
                    break

    # no bracket
    if strong == -1 and weak == len(chain):
        bracket = -1

    # one-sided brackets
    elif strong == -1:
        bracket = [chain[weak], None]
    elif weak == len(chain):
        bracket = [None, chain[strong]]

    # bracket found
    else:
        bracket = [chain[weak], chain[strong]]

    return bracket


# finding all the brackets
def main():
    # get the chain decomposition
    chains_df = pd.read_csv(CSV_FILE)
    chains_list = []
    [chains_list.append(row) for row in chains_df]
    chains_list = chains_df.values.tolist()

    for i, c in enumerate(chains_list):
        chains_list[i] = list(filter(lambda a: pd.notna(a), c))
    input_chains = [[str(s) + ".in" for s in c] for c in chains_list]

    # get the bracket from each chain
    all_brackets = []
    for i, chain in enumerate(input_chains):
        bracket = find_bracket(chain)
        if bracket != -1:
            all_brackets.append(bracket)

    return all_brackets


if __name__ == "__main__":
    print(main())

