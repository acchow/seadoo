from p9_tools.parse import theory
from p9_tools import config


def alpha_constants(lines):
    for i, line in enumerate(lines):
        if "(" in line and ")" in line and \
                "formulas(assumptions)" not in line and "end_of_list" not in line:

            bracket_contents = line[line.index("(")+1:line.index(")")]
            for j, c in enumerate(bracket_contents):
                if c != "," and not c.isalpha():
                    lines[i] = lines[i].replace(c, chr(int(c)+97))      # replace with alphabet letter

    return lines


def extract_constants(lines):
    unique_constants = []
    for i, line in enumerate(lines):
        if "(" in line and ")" in line and \
                "formulas(assumptions)" not in line and "end_of_list" not in line:

            bracket_contents = line[line.index("(")+1:line.index(")")]
            constants = bracket_contents.split(",")
            for c in constants:
                if c not in unique_constants:
                    unique_constants.append(c)
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


def closure_axiom(unique_constants):
    equalities = ""
    for c in unique_constants:
        temp = "(x=" + c + ")|"
        equalities += temp
    equalities = equalities.rstrip(equalities[-1])   # remove the last or symbol
    axiom = ["(all x (" + equalities + "))"]
    print(axiom)
    return axiom


def model_setup(file_name, closed_world=False):
    with open(file_name, "r") as f:
        model_spec_lines = f.readlines()
        del model_spec_lines[0]                         # formulas(assumptions)
        del model_spec_lines[len(model_spec_lines)-1]   # end_of_list

        # remove comments
        model_spec_lines = [x for x in model_spec_lines if "%" not in x and x != "\n" and x != ""]

        model_spec_lines = alpha_constants(model_spec_lines)
        constants = extract_constants(model_spec_lines)

        # add inequalities for constants
        inequalities = make_inequalities(constants)
        model_spec_lines += inequalities

        if closed_world:
            # add closure axiom
            closure = closure_axiom(constants)
            model_spec_lines += closure

        symbols_to_remove = [".\n", "\n", "\t"]
        for s in symbols_to_remove:
            model_spec_lines = theory.replace_symbol(model_spec_lines, s, "")

    f.close()
    return model_spec_lines


if __name__ == "__main__":
    print(model_setup(config.model))

