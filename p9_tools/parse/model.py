from p9_tools.parse import theory
from itertools import permutations
import config
import re


def alpha_constants(lines):
    for i, line in enumerate(lines):
        if "(" in line and ")" in line and "formulas(assumptions)" not in line and "end_of_list" not in line:
            bracket_contents = line[line.index("(")+1:line.index(")")]
            for j, c in enumerate(bracket_contents):
                if c.isnumeric():
                    lines[i] = lines[i].replace(c, chr(int(c)+97))      # replace with alphabet letter

    return lines


def extract_constants(lines):
    unique_constants = []
    for i, line in enumerate(lines):
        if "(" in line and ")" in line and "formulas(assumptions)" not in line and "end_of_list" not in line:  
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
        s = pair[0] + "!=" + pair[1]
        statements.append(s)
    return statements


def closed_model(model_lines, unique_constants, signature, num_args): 
    closed = []

    # add -signature(x,y) for all x,y
    perms = permutations(unique_constants, num_args)
    for p in perms: 
        args = ','.join(p)
        negated = '-' + signature + '(' + args + ')'
        if negated[1:] not in model_lines: 
            closed.append(negated)
    
    # add -signature(x,x) for all x
    for c in unique_constants: 
        negated = '-' + signature + '(' + c + ',' + c + ')'
        if negated[1:] not in model_lines: 
            closed.append(negated)

    # closure axiom
    equalities = ""
    for c in unique_constants:
        temp = "(x=" + c + ")|"
        equalities += temp
    equalities = equalities.rstrip(equalities[-1])   # remove the last or symbol
    closed.append("(all x (" + equalities + "))")

    return closed


# function to identify the definitions required to pull from
# parsing all the signatures that appear before an opening parentheses
def extract_signatures(lines: list[str]) -> dict:
    s = {}
    for line in lines:
        i = line.find('(')
        j = line.find(')')

        # assertion
        if j > i and i != -1 and j != -1: 
            signature = line[:i] if line[0] != '-' else line[1:i]
            args = line[i+1:j].split(",")
            if re.match('^[a-zA-Z0-9_]+$', signature): 
                if signature not in s: 
                    s[signature] = {
                        'args': len(args),      #arguments
                        'asser': [line]         #assertions
                    }
                else: 
                    s[signature]['asser'].append(line)
    return s


def model_setup(file_name, closed_world=True):
    with open(file_name, "r") as f:
        model_spec_lines = f.readlines()
        model_spec_lines = [x for x in model_spec_lines if "%" not in x and x != "\n" and x != "" and "formulas(assumptions)" not in x and "end_of_list" not in x]

        model_spec_lines = alpha_constants(model_spec_lines)
        constants = extract_constants(model_spec_lines)

        # add inequalities for constants
        inequalities = make_inequalities(constants)
        model_spec_lines += inequalities
        
        symbols_to_remove = [".\n", "\n", "\t"]
        for s in symbols_to_remove:
            model_spec_lines = theory.replace_symbol(model_spec_lines, s, "")
            
        # closed world assumption
        if closed_world:
            signatures = extract_signatures(model_spec_lines)
            for s in signatures:
                closed_lines = closed_model(signatures[s]['asser'], constants, s, signatures[s]['args'])
                model_spec_lines += closed_lines

    f.close()
    return model_spec_lines, constants


if __name__ == "__main__":
    print(model_setup(config.model))

