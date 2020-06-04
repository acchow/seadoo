import requests
import nltk
from nltk.sem.drt import DrtParser
from nltk.sem import logic
logic._counter._value = 0

# checks consistency and entailment between two ontologies

ontology1 = input("file name of ontology 1: ")
ontology2 = input("file name of ontology 2: ")

with open(ontology2, "r") as file:
    lines = file.readlines()

lines.remove("formulas(assumptions).\n")
lines.remove("end_of_list.\n")
axioms = list(filter(lambda x: x != "\n", lines))

# print(axioms)

index_lastLine = []
for c, val in enumerate(lines):
    if "." in val:
        index_lastLine.append(c)
        # print(val)
        # print(str(c) + ", " + val)

# print(index_lastLine)

one_axiom = []
all_axioms = []
c2 = 0
# counted loop from zero to the length of index_lastLine list
for c1, i in enumerate(index_lastLine):
    # counted loop from counter k to next value in index_lastLine
    while c2 <= i:
        one_axiom.append(lines[c2])
        c2 += 1
    all_axioms.append("\n".join(one_axiom))
    one_axiom.clear()

# print(all_axioms)
# print("\n\n length: ", len(all_axioms))

# counted loop to new file for each axiom
for num, axiom in enumerate(all_axioms, 1):
    new_filename = "axiom_"+str(num)+".in"
    with open(new_filename,"w+") as newfile:
        newfile.write(axiom)

file.close()





