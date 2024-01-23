import os
import config

DEFINITIONS_PATH = config.definitions


def concatenate_axioms(lines):
    # remove specific lines
    [lines.remove(x) for x in lines if "formulas(assumptions)" in x]
    [lines.remove(y) for y in lines if "end_of_list" in y]

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


def theory_setup(theory_name):
    try:
        with open(theory_name, "r") as f:
            lines = f.readlines()
            lines = concatenate_axioms(lines)

            # remove comments
            
            for i in range(len(lines)):
                if "%" in lines[i]:
                    idx = lines[i].find("%")
                    idx2 = lines[i].find("\n",idx+2)
                    lines[i] = lines[i][idx2:]
            lines = [x for x in lines if x != "\n" and x != ""]
        
            replace_symbol(lines, ".", "")      # added this for definitions
            replace_symbol(lines, ".\n", "")
            replace_symbol(lines, "\t", "")
        f.close()
    except FileNotFoundError:
        print("file", theory_name, "not found")
        return False
    return lines


# function to identify the definitions required to pull from
# parsing all the signatures that appear before an opening parentheses
def signatures(lines):
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


# retrieve definitions given a relation signature
def definitions(signature):
    file_name = str(signature) + ".in"
    lines = []

    for definition_file in os.listdir(DEFINITIONS_PATH):
        if definition_file == file_name:
            lines = theory_setup(os.path.join(os.path.sep, DEFINITIONS_PATH, definition_file))

    return lines




