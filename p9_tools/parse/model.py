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


def model_setup(file_name):
    with open(file_name, "r") as f:
        model_spec_lines = f.readlines()
        del model_spec_lines[0]         # formulas(assumptions)
        del model_spec_lines[len(model_spec_lines)-1] # end_of_list

        # remove comments
        for x, line in enumerate(model_spec_lines):
            while "%" in line:
                model_spec_lines.remove(model_spec_lines[x])

        try:
            while True:
                model_spec_lines.remove("\n")
        except ValueError:
            pass
        try:
            while True:
                model_spec_lines.remove("")
        except ValueError:
            pass

        model_spec_lines = alpha_constants(model_spec_lines)
        inequalities = make_inequalities(extract_constants(model_spec_lines))
        model_spec_lines += inequalities

        model_spec_lines = theory.replace_symbol(model_spec_lines, ".\n", "")
        model_spec_lines = theory.replace_symbol(model_spec_lines, "\n", "")
        model_spec_lines = theory.replace_symbol(model_spec_lines, "\t", "")

    f.close()
    return model_spec_lines


if __name__ == "__main__":
    print(model_setup(config.model))

