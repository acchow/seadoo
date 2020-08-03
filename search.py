# accepts file with model specification
# extract constants
# add inequalities for each pair of constants
# insert that as a theory
# return the "closest existing theory"


def extract_constants(lines):
    unique_constants = []
    for line in lines:
        if "(" in line:
            for c in range(line.index("(")+1, line.index(")")-1, 1):
                while line[c] != "," and line[c] not in unique_constants:
                    unique_constants.append(line[c])
    return unique_constants


def make_inequalities(unique_constants):
    # num_pairs = (len(unique_constants)*(len(unique_constants)-1))/2
    pairs = []

    # find all pairs
    for i in range(0, len(unique_constants)-1, 1):
        for j in range(i+1, len(unique_constants), 1):
            pairs.append([unique_constants[i], unique_constants[j]])
    # print(pairs)

    # create list of statements with the pairs
    statements = []
    for pair in pairs:
        s = pair[0] + "!=" + pair[1] + ".\n"
        statements.append(s)
    # print(statements)
    return statements


def main(file_name):
    with open(file_name, "r+") as f:
        lines = f.readlines()

        input1 = (extract_constants(lines))
        add_these_lines = make_inequalities(input1)

        f.write("\n\n")
        for line in add_these_lines:
            f.write(line)

    f.close()
    print("done")


main("anti_strict_model_spec.in")
