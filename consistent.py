import requests
import nltk
from nltk import Prover9

from nltk import *
from nltk.sem.drt import DrtParser
from nltk.sem import logic

from nltk.sem import Expression
read_expr = Expression.fromstring

# logic._counter._value = 0

# -------------------------
# this program checks consistency and entailment between two ontologies
# -------------------------


def concatenate_axioms(lines):
    # clean up list
    lines.remove("formulas(assumptions).\n")
    lines.remove("end_of_list.\n")

    for x, line in enumerate(lines):
        while "%" in lines[x]:
            lines.remove(lines[x])

    try:
        while True:
            lines.remove("\n")
    except ValueError:
        pass

    # put axioms together into one list
    index_last_line = []
    for c, val in enumerate(lines):
        if "." in val:
            index_last_line.append(c)

    one_axiom = []
    all_axioms = []
    c2 = 0
    for c1, i in enumerate(index_last_line):
        while c2 <= i:
            one_axiom.append(lines[c2])
            c2 += 1
        all_axioms.append("".join(one_axiom))
        one_axiom.clear()

    return all_axioms


def replace_symbol(lines, symbol, new_symbol):
    for x, line in enumerate(lines):
        while symbol in lines[x]:
            lines[x] = line.replace(symbol, new_symbol)
    return lines


def create_file(name, contents):
    with open(name, "w+") as new_file:
        new_file.write(contents)


def consistency(lines_o1, lines_o2):
    lines = lines_o1 + lines_o2
    assumptions = read_expr(lines[0])
    mb = MaceCommand(None, [assumptions])

    # add axioms into assumptions
    for c, added in enumerate(lines):
        if c == 0:
            continue
        mb.add_assumptions([read_expr(added)])

    # use mb.build_model([assumptions]) to print the input
    model = mb.build_model()

    if model:
        consistent = True
        consistent_model = mb.model(format='cooked')
        # print("o1 and o2 are consistent, here's the model constructed by mace: \n", consistent_model)
        # create_file("consistency_model_" + ontology1 + "_and_" + ontology2, c_model)
    else:
        consistent = False
        # print("o1 and o2 are not mutually consistent")

    return consistent


def entailment(lines_o1, lines_o2):
    saved_proofs = []
    saved_models = []
    entail = 0

    for c1, goal in enumerate(lines_o2):

        # set first lines to use prover
        assumptions = read_expr(lines_o1[0])

        goals = read_expr(goal)

        prover = Prover9Command(goals, [assumptions])

        # add axioms into assumptions
        for c, added in enumerate(lines_o1):
            if c == 0:
                continue
            prover.add_assumptions([read_expr(added)])

        print("from prover9, assumptions: \n", prover.assumptions())
        print("from p9, the goal: \n", prover.goal())

        proven = prover.prove()
        # print("is there proof? ", proven)

        if proven & (entail == 0):
            get_proof = prover.proof()
            saved_proofs.append(get_proof)
            print(get_proof)

        elif proven is False:
            entail += 1
            # saved_proofs.clear()

            print("no entailment, here's a counterexample: ")
            mb = MaceCommand(goals, [assumptions])
            for c, added in enumerate(lines_o1):
                if c == 0:
                    continue
                mb.add_assumptions([read_expr(added)])

            print("from mace, assumptions: \n", mb.assumptions())
            print("from mace, the goal: \n", mb.goal())

            # use mb.build_model([assumptions]) to print the input
            # is there a counterexample?
            counterexample = mb.build_model()

            if counterexample:
                get_model = mb.model(format='cooked')
                saved_models.append(get_model)
                print("model constructed by mace: \n", get_model)
            elif counterexample is False:
                print("no counterexample found for the axiom: \n", mb.goal())

    if entail > 0:
        # for c, model in enumerate(saved_models):
        #     create_file("model"+str(c), model)
        return False
    else:
        # for c, proof in enumerate(saved_proofs):
        #     create_file("proof"+str(c), proof)
        return True


# main program

ontology1 = input("file name of ontology 1: ")
ontology2 = input("file name of ontology 2: ")

with open(ontology1, "r") as file1:
    lines1 = file1.readlines()

with open(ontology2, "r") as file2:
    lines2 = file2.readlines()

lines1 = concatenate_axioms(lines1)
lines2 = concatenate_axioms(lines2)
replace_symbol(lines1, ".\n", "")
replace_symbol(lines1, "\t", "")
replace_symbol(lines2, ".\n", "")
replace_symbol(lines2, "\t", "")

# print("from lines1: \n", lines1, "\n\n")
# print("from lines2: \n", lines2, "\n\n")

if consistency(lines1, lines2):

    print("o1 and o2 are consistent! file of model created. lets check entailment: ")
    o1_entails_o2 = entailment(lines1, lines2)
    o2_entails_o1 = entailment(lines2, lines1)

    if o1_entails_o2:
        print("ontology1 entails ontology 2")

    if o2_entails_o1:
        print("ontology2 entails ontology 1")

    if o1_entails_o2 & o2_entails_o1:
        print("o1 and o2 are equivalent!")
    elif (o1_entails_o2 is False) & (o2_entails_o1 is False):
        print("o1 and o2 are independent of each other")

else:
    print("o1 and o2 are not consistent!")


file1.close()
file2.close()
