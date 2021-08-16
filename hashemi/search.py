from nltk import *

import pandas as pd
from p9_tools import config
from p9_tools.relationship import relationship, files
from p9_tools.parse import theory, model
import os

from nltk.sem import Expression
read_expr = Expression.fromstring

FILE_PATH = config.path
EX_PATH = config.examples
CEX_PATH = config.counterexamples
TRANSLATIONS = config.translations
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


# function to identify the definitions required to pull from
# parsing all the signatures that appear before an opening parentheses
def extract_signatures(lines):
    s = set()

    for axiom in lines:
        for i, char in enumerate(axiom):
            if char == "(" and axiom[i-1].isalpha():
                j = i-1
                signature = ""
                # accounts for signatures containing letters, numbers and underscores
                while (axiom[j].isalpha() or axiom[j].isnumeric() or axiom[j] == "_") and j >= 0:
                    signature = axiom[j] + signature    # appending letter to the front of string
                    j -= 1
                if signature:
                    s.add(signature)
    return s


# retrieve translation definitions given a relation signature
def translation_definitions(signature):
    file_name = str(signature) + ".in"
    # lines = []
    definition = []     # to account for blank lines

    for definition_file in os.listdir(TRANSLATIONS):
        if definition_file == file_name:
            with open(os.path.join(os.path.sep, TRANSLATIONS, definition_file), "r+") as f:
                definition = theory.theory_setup(os.path.join(os.path.sep, TRANSLATIONS, definition_file))
            # lines = theory_setup(os.path.join(os.path.sep, DEFINITIONS_PATH, definition_file))

    return definition


def find_bracket(chain):
    strong = len(chain)-1       # maximum index for strongest theory for examples
    weak = 0                    # minimum index for weakest theory for counterexamples

    # find strongest theory that is consistent with all examples
    for ex_file in os.listdir(EX_PATH):
        if ex_file.endswith(".in"):
            print("ex", ex_file)
            # print(model.model_setup(os.path.join(EX_PATH, ex_file), closed_world=True))

            model_lines = model.model_setup(os.path.join(EX_PATH, ex_file), closed_world=True)
            signatures = extract_signatures(model_lines)
            for s in signatures:
                model_lines += translation_definitions(s)

            print(model_lines)

            s = find_strong(chain, model_lines)
            # s = find_strong(chain, model.model_setup(os.path.join(EX_PATH, ex_file), closed_world=True))
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
            # print(model.model_setup(os.path.join(CEX_PATH, cex_file), closed_world=True))

            model_lines = model.model_setup(os.path.join(CEX_PATH, cex_file), closed_world=True)
            signatures = extract_signatures(model_lines)
            for s in signatures:
                model_lines += translation_definitions(s)

            print(model_lines)

            w = find_weak(chain, model_lines)
            # w = find_weak(chain, model.model_setup(os.path.join(CEX_PATH, cex_file), closed_world=True))
            # update the minimum
            if w > weak:
                weak = w
                # the counterexample is consistent with all theories in the chain
                if weak == len(chain):
                    break

    # no bracket
    if strong == -1 and weak == len(chain):
        bracket = [None, None]

    # one-sided brackets
    elif strong == -1:
        bracket = [weak, None]
    elif weak == len(chain):
        bracket = [None, strong]

    # bracket found
    else:
        bracket = [weak, strong]
    return bracket


def setup_bracket_model(t_weak_name, t_to_negate_axioms):
    print("t_weak", t_weak_name)
    print("t_negate_axioms", t_to_negate_axioms)

    t_weak = theory.theory_setup(t_weak_name)
    t_negate = theory.theory_setup(t_to_negate_axioms)

    negated_axioms = []
    for i, axiom in enumerate(t_negate):
        negated = ["-(" + axiom + ")"]

        if relationship.consistency(t_weak, negated, new_dir=""):
            negated_axioms += negated

    theory_lines = t_weak + negated_axioms
    return theory_lines


def generate_model(theory_lines, new_dir, file_name):
    print(theory_lines)
    assumptions = read_expr(theory_lines[0])

    # look for 10 models before timeout
    mb = MaceCommand(None, [assumptions], max_models=10)
    for c, added in enumerate(theory_lines[1:]):
        mb.add_assumptions([read_expr(added)])

    # use mb.build_model([assumptions]) to print the input
    # consistent = "inconclusive"
    try:
        model = mb.build_model()
        # found a model, the theories are consistent with each other
        if model:
            # consistent = True
            consistent_model = mb.model(format='cooked')
            if new_dir:
                files.create_file(new_dir, file_name, consistent_model)
            return True
    except LogicalExpressionException:
        print("input error")
    else:
        print("model not found")

    return False


def get_input_chains():
    chains_df = pd.read_csv(CSV_FILE)
    chains_list = []
    [chains_list.append(row) for row in chains_df]
    chains_list = chains_df.values.tolist()

    for i, c in enumerate(chains_list):
        chains_list[i] = list(filter(lambda a: pd.notna(a), c))
    input_chains = [[str(s) + ".in" for s in c] for c in chains_list]
    return input_chains


# finding all the brackets
def main():
    # chain decomposition in list form
    input_chains = get_input_chains()

    # get the bracket from each chain
    all_brackets = []
    for i, chain in enumerate(input_chains):
        bracket = [i] + find_bracket(chain)
        all_brackets.append(bracket)

    # singular best matches
    best_match_axioms = set()

    # bracket union
    lb_axioms = set()
    ub_axioms = set()

    # answer report
    answer_report = ["seadoo hashemi answer report\n\n"]

    try:
        new_dir = os.path.join(FILE_PATH, "models_to_classify")
        os.mkdir(new_dir)
    except FileExistsError:
        new_dir = os.path.join(FILE_PATH, "models_to_classify")

    for bracket in all_brackets:
        if bracket[1] is None or bracket[2] is None:
            print("no bracket found for chain", bracket[0])
            best_match = None
        else:
            # dialogue phase

            # refine upper bound
            ub_min = False
            lb_theory = input_chains[bracket[0]][bracket[1]]
            while ub_min is False and bracket[2] > 0:
                ub_theory = input_chains[bracket[0]][bracket[2]]
                ub_model = "ub_model_" + lb_theory.replace(".in", "") + "_" + ub_theory.replace(".in", "")
                # look for a model
                if generate_model(setup_bracket_model(os.path.join(FILE_PATH, lb_theory),
                                                      os.path.join(FILE_PATH, ub_theory)),
                                  os.path.join(FILE_PATH, new_dir),
                                  ub_model):
                    ans = input("is " + os.path.join(new_dir, ub_model) + " an example? (y/n):")
                    # omits a model
                    if ans == 'y':
                        bracket[2] -= 1
                    else:
                        ub_min = True
                else:
                    print("model cannot be generated for ", ub_model)
                    ub_min = True

            # refine lower bound
            lb_max = False
            # while lb_max is False and bracket[1] < bracket[2]:
            while lb_max is False and bracket[1] < len(input_chains[bracket[0]])-1:
                lb_theory = input_chains[bracket[0]][bracket[1]]
                lb_theory_next = input_chains[bracket[0]][bracket[1] + 1]   # subsequent theory in the chain
                lb_model = "lb_model_" + lb_theory.replace(".in", "") + "_" + lb_theory_next.replace(".in", "")
                # look for a model
                if generate_model(setup_bracket_model(os.path.join(FILE_PATH, lb_theory),
                                                      os.path.join(FILE_PATH, lb_theory_next)),
                                  os.path.join(FILE_PATH, new_dir),
                                  lb_model):
                    ans = input("is " + os.path.join(new_dir, lb_model) + " an example? (y/n):")
                    # contains an unintended model
                    if ans == 'n':
                        bracket[1] += 1  # move lower bound up
                    else:
                        lb_max = True
                else:
                    print("model cannot be generated for ", lb_model)
                    lb_max = True

            if bracket[1] == bracket[2]:
                best_match = input_chains[bracket[0]][bracket[1]]
                for axiom in theory.theory_setup(os.path.join(FILE_PATH, best_match)):
                    best_match_axioms.add(axiom)
                print("best matching theory from chain", bracket[0] + 1, "is", best_match)
            elif bracket[1] > bracket[2]:
                best_match = None
                print("overlapped bracket, theory does not exist in chain", bracket[0] + 1)
            else:
                best_match = [input_chains[bracket[0]][bracket[1]], input_chains[bracket[0]][bracket[2]]]
                for axiom in theory.theory_setup(os.path.join(FILE_PATH, input_chains[bracket[0]][bracket[1]])):
                    lb_axioms.add(axiom)
                for axiom in theory.theory_setup(os.path.join(FILE_PATH, input_chains[bracket[0]][bracket[2]])):
                    ub_axioms.add(axiom)
                print("bracket from chain", bracket[0] + 1, best_match, "cannot be further refined")
            answer_report.append("chain " + str(bracket[0] + 1) + ": " + str(best_match) + "\n")

    # final answer
    # best match axioms
    if best_match_axioms:
        answer_report.append("\n\nbest matching theory found:\n")
        print("best matching theory: ")
        for axiom in best_match_axioms:
            answer_report.append(axiom + ".")
            print(axiom)

    # union of brackets
    elif lb_axioms and ub_axioms:
        answer_report.append("\n\nbest matching bracket found:\n")
        print("best matching bracket")

        answer_report.append("\nlower bound:")
        print("lower bound: ")
        for axiom in lb_axioms:
            answer_report.append(axiom + ".\n")
            print(axiom)

        answer_report.append("\n\nupper bound:")
        print("upper bound: ")
        for axiom in ub_axioms:
            answer_report.append(axiom + ".\n")
            print(axiom)

    # no matches
    else:
        answer_report.append("\n\nno best match exists")
        print("no best match exists")

    with open("test_answer_report.txt", "w") as f:
        for line in answer_report:
            f.write(line)

    return answer_report


if __name__ == "__main__":
    main()

