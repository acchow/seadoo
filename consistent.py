import requests
import nltk
from nltk import Prover9, TableauProver, ResolutionProver

from nltk import *
from nltk.sem.drt import DrtParser
from nltk.sem import logic

from nltk.sem import Expression
read_expr = Expression.fromstring

# logic._counter._value = 0

# -------------------------
# this program checks consistency and entailment between two ontologies
# -------------------------

ontology1 = input("file name of ontology 1: ")
ontology2 = input("file name of ontology 2: ")

with open(ontology1, "r") as file1:
    lines_o1 = file1.readlines()

with open(ontology2, "r") as file2:
    lines_o2 = file2.readlines()


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


def replace_symbol(lines, symbol, newsymbol):
    for x, line in enumerate(lines):
        while symbol in lines[x]:
            lines[x] = line.replace(symbol, newsymbol)
    return lines


lines_o1 = concatenate_axioms(lines_o1)
lines_o2 = concatenate_axioms(lines_o2)

replace_symbol(lines_o1, ".\n", "")
replace_symbol(lines_o1, "\t", "")
# replace_symbol(lines_o1, "\n", "")

# lines_o1 = "\n".join(lines_o1)

replace_symbol(lines_o2, ".\n", "")
replace_symbol(lines_o2, "\t", "")
# replace_symbol(lines_o2, "\n", "")



# --------------- creates new file for each axiom ---------------
# for num, axiom in enumerate(lines_o2, 1):
#     new_filename = "axiom_"+str(num)+".in"
#     with open(new_filename, "w+") as new_file:
#         new_file.write(axiom)

# The prove() method takes three optional arguments: a goal,
# a list of assumptions, and a verbose boolean to indicate whether
# the proof should be printed to the console.
# Example:

# p1 = read_expr('man(socrates)')
# print(p1)
# p2 = read_expr('all x (man(x) -> mortal(x))')
# print(p2)
# c = read_expr('all x\n\t(mortal(x))\n')
# print(c)
# Prover9().prove(c, [p1,p2], verbose=True)

print("from lines_o1: \n", lines_o1, "\n\n")
print("from lines_o2: \n", lines_o2, "\n\n")

# check entailment

def entailment (lines_o1, lines_o2):



     # print("here are all assumptions:\n")
        # prover.print_assumptions("Prover9")
        # print("\n")

    for c1, goal in enumerate(lines_o2):

        # # set first lines to use prover
        assumptions = read_expr(lines_o1[0])

        goals = read_expr(goal)

        prover = Prover9Command(goals, [assumptions])

        # add axioms into assumptions
        for c, added in enumerate(lines_o1):
            if c == 0:
                continue
            prover.add_assumptions([read_expr(added)])

        print("from prover9, assumptions: \n", prover.assumptions())
        print("\nfrom p9, the goal: \n",prover.goal())

        proven = prover.prove()
        print("is there proof? ", proven)
        print(prover.proof())

        if proven is False:
            print("no entailment")
            entail = False
            break
        else:
            entail = True

    return entail


o1_entails_o2 = entailment(lines_o1, lines_o2)
o2_entails_o1 = entailment(lines_o2, lines_o1)

if o1_entails_o2:
    print("ontology1 entails ontology 2!")
else:
    print("o1 does not entail o2!")

if o2_entails_o1:
    print("ontology2 entails ontology 1!")
else:
    print("o2 does not entail o1!")

if o1_entails_o2 & o2_entails_o1:
    print("o1 and o2 are consistent!")
else:
    print("o1 and o2 are not consistent!")


file1.close()
file2.close()
