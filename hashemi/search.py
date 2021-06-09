import pandas as pd
import config
from relationship import relationship
from parse import theory, model
import os


# find the strongest theory in the chain that is consistent with the example
def find_strong(chain, model_lines):
    i = len(chain)-1    # starting index from the end
    consistent = False
    strongest = -1       # index of strongest consistent theory

    while i >= 0 and not consistent:
        consistent = relationship.consistency(model_lines, theory.theory_setup(config.path + "/" + chain[i]))
        # found maximal consistent theory
        if consistent:
            strongest = i
            break
        i -= 1

    return strongest


# find weakest theory that is not consistent with the counterexample
def find_weak(chain, model_lines):
    i = 0
    max_index = len(chain)-1
    consistent = True
    weakest = len(chain)

    while i <= max_index and consistent:
        consistent = relationship.consistency(model_lines, theory.theory_setup(config.path + "/" + chain[i]))
        # found minimal inconsistent theory
        if not consistent:
            weakest = i
            break
        i += 1

    return weakest


def find_bracket(chain, ex_path=config.examples, cex_path=config.counterexamples):
    strong = len(chain)-1       # maximum index for strongest theory for examples
    weak = 0                    # minimum index for weakest theory for counterexamples

    # find strongest theory that is consistent with all examples
    for ex_file in os.listdir(ex_path):
        if ex_file.endswith(".in"):
            s = find_strong(chain, model.model_setup(ex_path + "/" + ex_file))
            # update the maximum
            if s < strong:
                strong = s
                # the example is inconsistent with all theories in the chain
                if strong == -1:
                    break

    # find weakest theory that is not consistent with all counterexamples
    for cex_file in os.listdir(cex_path):
        if cex_file.endswith(".in"):
            w = find_weak(chain, model.model_setup(cex_path + "/" + cex_file))
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
def main(csv_file=config.csv, ex_path=config.examples, cex_path=config.counterexamples):
    # get the chain decomposition
    chains_df = pd.read_csv(csv_file)
    chains_list = []
    [chains_list.append(row) for row in chains_df]
    chains_list = chains_df.values.tolist()

    for i, c in enumerate(chains_list):
        chains_list[i] = list(filter(lambda a: pd.notna(a), c))
    input_chains = [[str(s) + ".in" for s in c] for c in chains_list]

    # get the bracket from each chain
    all_brackets = []
    for i, chain in enumerate(input_chains):
        bracket = find_bracket(chain, ex_path, cex_path)
        if bracket != -1:
            all_brackets.append(bracket)

    return all_brackets


print(main())

