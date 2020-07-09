import requests
import nltk
from nltk import Prover9
# import os
# import shutil

from nltk import *
from nltk.sem.drt import DrtParser
from nltk.sem import logic

from nltk.sem import Expression
read_expr = Expression.fromstring

# logic._counter._value = 0

# -------------------------
# this program finds the relationship between two ontologies/theories
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


def create_file(name, contents, path):
    new_path = os.path.join(path, name)
    with open(new_path, "w+") as new_file:
        new_file.write(contents)


def consistency(lines_o1, lines_o2, path):
    lines = lines_o1 + lines_o2
    assumptions = read_expr(lines[0])
    mb = MaceCommand(None, [assumptions])
    prover = Prover9Command(None, [assumptions])

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
        create_file("consistent_model", consistent_model, path)
    else:
        for c, added in enumerate(lines):
            if c == 0:
                continue
            prover.add_assumptions([read_expr(added)])
        consistent = False
        inconsistent_model = prover.proof()
        # print("o1 and o2 are mutually inconsistent, here's the proof: \n", inconsistent_model)
        create_file("inconsistent_proof", inconsistent_model, path)

    return consistent


def entailment(lines_o1, lines_o2, path):
    saved_proofs = []
    new_axioms = []
    entail = 0
    counter_file_created = False

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

        # print("from prover9, assumptions: \n", prover.assumptions())
        # print("from p9, the goal: \n", prover.goal())

        proven = prover.prove()
        # print("is there proof? ", proven)

        if proven & (entail == 0):
            get_proof = prover.proof()
            saved_proofs.append(get_proof)
            # print(get_proof)

        elif proven is False:
            entail += 1
            # saved_proofs.clear()

            # print("no entailment, here's a counterexample: ")
            mb = MaceCommand(goals, [assumptions])
            for c, added in enumerate(lines_o1):
                if c == 0:
                    continue
                mb.add_assumptions([read_expr(added)])

            # print("from mace, assumptions: \n", mb.assumptions())
            # print("from mace, the goal: \n", mb.goal())

            # use mb.build_model([assumptions]) to print the input
            # is there a model?
            counterexample = mb.build_model()
            new_axioms.append(mb.goal())

            if counterexample & (counter_file_created is False):
                counterexample_model = mb.model(format='cooked')
                create_file("counterexample_found", counterexample_model, path)
                counter_file_created = True
                # print("model constructed by mace, file created : \n", counterexample_model)
            # elif counterexample is False:
            #     print("no counterexample found for the axiom: \n", mb.goal())

    if entail > 0:
        # create_file("remaining_axioms", new_axioms, path)
        return False
    else:
        for c, proof in enumerate(saved_proofs):
            create_file("proof"+str(c+1), proof, path)
        return True


# xml syntax for .owl files
def create_xml(t_1, rel, t_2, visual=False):
    if visual:
        l1 = "ObjectPropertyAssertion(:" + rel
        l2 = " :" + t_1 + " :" + t_2 + ")\n\n"
        return l1 + l2
    else:
        l1 = "# Individual: :" + t_1 + " (:" + t_1 + ")\n\n"
        l2 = "ClassAssertion(:Theory :" + t_1 + ")\n\n"

        l3 = "# Individual: :" + t_2 + " (:" + t_2 + ")\n\n"
        l4 = "ClassAssertion(:Theory :" + t_2 + ")\n"

        l5 = "ObjectPropertyAssertion(:" + rel + " :" + t_1 + " :" + t_2 + ")\n\n"
        return l1 + l2 + l3 + l4 + l5


def oracle(t1, lines_t1, t2, lines_t2, path, owl_file, owl_visual):
    if consistency(lines_t1, lines_t2, path):
        # print("o1 and o2 are consistent! lets check entailment: ")
        o1_entails_o2 = entailment(lines_t1, lines_t2, path)
        o2_entails_o1 = entailment(lines_t2, lines_t1, path)

        if o1_entails_o2 & o2_entails_o1:
            owl_file.write(create_xml(t1, "equivalent", t2))
            owl_visual.write(create_xml(t1, "equivalent", t2, True))
            # print("o1 and o2 are equivalent!")
            os.rename(path, t1 + "_equivalent_" + t2)
            return "equivalent"

        elif (o1_entails_o2 is False) & (o2_entails_o1 is False):
            owl_file.write(create_xml(t1, "independent", t2))
            owl_visual.write(create_xml(t1, "independent", t2, True))
            # print("o1 and o2 are independent of each other")
            os.rename(path, t1 + "_independent_" + t2)
            return "independent"

        elif o1_entails_o2:
            owl_file.write(create_xml(t1, "entails", t2))
            owl_visual.write(create_xml(t1, "entails", t2, True))
            # print("ontology1 entails ontology 2")
            os.rename(path, t1 + "_entails_" + t2)
            return "t1_entails_t2"

        elif o2_entails_o1:
            owl_file.write(create_xml(t2, "entails", t1))
            owl_visual.write(create_xml(t2, "entails", t1, True))
            # print("ontology2 entails ontology 1")
            os.rename(path, t2 + "_entails_" + t1)
            return "t2_entails_t1"

    elif consistency(lines_t1, lines_t2, path) is False:
        owl_file.write(create_xml(t1, "inconsistent", t2))
        owl_visual.write(create_xml(t1, "inconsistent", t2, True))
        # print("o1 and o2 are not consistent!")
        os.rename(path, t1 + "_inconsistent_" + t2)
        return "inconsistent"


# main program
def main_program(t1, t2):
    with open(t1, "r") as file1:
        lines_t1 = file1.readlines()

    with open(t2, "r") as file2:
        lines_t2 = file2.readlines()

    owl_file = open("metatheory.owl", "a+")
    owl_visual = open("alt-metatheory.owl", "a+")

    t1 = t1.replace(".in", "")
    t2 = t2.replace(".in", "")

    # for files in os.listdir():
    #     possible = [t1 + "_inconsistent_" + t2]
    #     if files is one of the possibilities
    #         relationship = files.replace(t1, "t1").replace(t2, "t2")
    #         return relationship

    new_dir = t1 + "_" + t2
    # should be if file name has both t1 and t2 instead of os.path.exists
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)

    lines_t1 = concatenate_axioms(lines_t1)
    lines_t2 = concatenate_axioms(lines_t2)
    replace_symbol(lines_t1, ".\n", "")
    replace_symbol(lines_t1, "\t", "")
    replace_symbol(lines_t2, ".\n", "")
    replace_symbol(lines_t2, "\t", "")

    relationship = oracle(t1, lines_t1, t2, lines_t2, new_dir, owl_file, owl_visual)

    file1.close()
    file2.close()
    owl_file.close()

    return relationship


print(main_program("betweenness.in", "fishburn.in"))
