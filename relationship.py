from nltk import *
import os

from nltk.sem import Expression
read_expr = Expression.fromstring


def concatenate_axioms(lines):
    # remove specific lines
    [lines.remove(x) for x in lines if "formulas(assumptions)" in x]
    # [lines.remove("formulas(assumptions).\n") if "formulas(assumptions).\n" in lines else lines=lines]
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
    with open(theory_name, "r") as f:
        lines = f.readlines()
        lines = concatenate_axioms(lines)
        # remove comments
        for x, line in enumerate(lines):
            while "%" in lines[x]:
                lines.remove(lines[x])

        try:
            while True:
                lines.remove("\n")
        except ValueError:
            pass
        replace_symbol(lines, ".\n", "")
        replace_symbol(lines, "\t", "")
    f.close()
    return lines


def create_file(name, contents, path):
    new_path = os.path.join(path, name)
    with open(new_path, "w+") as new_file:
        new_file.write(contents)


def consistency(lines_t1, lines_t2, path=None):
    lines = lines_t1 + lines_t2
    assumptions = read_expr(lines[0])

    # look for 1 model before timeout
    mb = MaceCommand(None, [assumptions], max_models=10)
    for c, added in enumerate(lines[1:]):
        #if c == 0:
         #   continue
        mb.add_assumptions([read_expr(added)])

    # use mb.build_model([assumptions]) to print the input
    consistent = "inconclusive"
    try:
        model = mb.build_model()
        # found a model, the theories are consistent with each other
        if model:
            consistent = True
            consistent_model = mb.model(format='cooked')
            if path:
                create_file("consistent_model", consistent_model, path)

    except Exception:
        consistent = "inconclusive"  # inconclusive results so far, no model found



    #no model exists, or Mace reached max number of models
    if model is False:
        prover = Prover9Command(None, [assumptions], timeout=30)
        for c, added in enumerate(lines[1:]):
            #if c == 0:
             #   continue
            prover.add_assumptions([read_expr(added)])

        #try to find a proof for inconsistency
        try:
            proven = prover.prove()
            # proof found, result is inconsistent
            if proven:
                consistent = False
                inconsistent_proof = prover.proof()
                if path:
                    create_file("inconsistent_proof", inconsistent_proof, path)
            else:
                consistent = "inconclusive"
        except Exception:                   #proof timeout, reached max time limit
            consistent = "inconclusive"     #no model and no proof, inconclusive relationship

    return consistent


def entailment(lines_t1, lines_t2, path=None):
    saved_proofs = []
    entail = 0
    counter_file_created = False

    for c1, goal in enumerate(lines_t2):
        # set first lines to use prover
        assumptions = read_expr(lines_t1[0])
        goals = read_expr(goal)

        prover = Prover9Command(goals, [assumptions], timeout = 30)

        # add axioms into assumptions
        for c, added in enumerate(lines_t1[1:]):
            #if c == 0:
             #   continue
            prover.add_assumptions([read_expr(added)])

        # print("from prover9, assumptions: \n", prover.assumptions())
        # print("from p9, the goal: \n", prover.goal())

        proven = False
        proof_timeout = False
        #find proof of entailment for this axiom
        try:
            proven = prover.prove()
            if proven & (entail == 0):
                get_proof = prover.proof()
                saved_proofs.append(get_proof)
        except Exception:       #proof timeout, reached max time limit
            proof_timeout = True

        if proven is False:
            entail += 1
            # saved_proofs.clear()

            mb = MaceCommand(goals, [assumptions], max_models=10)
            for c, added in enumerate(lines_t1[1:]):
                #if c == 0:
                 #   continue
                mb.add_assumptions([read_expr(added)])

            # print("from mace, assumptions: \n", mb.assumptions())
            # print("from mace, the goal: \n", mb.goal())

            # use mb.build_model([assumptions]) to print the input
            try:
                counterexample = mb.build_model()

                #counterexample found. does not entail. create file for counterexample
                if counterexample & (counter_file_created is False):
                    counterexample_model = mb.model(format='cooked')
                    if path:
                        create_file("counterexample_found", counterexample_model, path)
                    counter_file_created = True

            except Exception:
                counterexample = False

            # new_axioms.append(mb.goal())

            #counterexample not found and no proof (dne or timed out), inconclusive results
            if counterexample is False and (proven is False or proof_timeout):
                return "inconclusive"


            # elif counterexample is False:
            #     print("no counterexample found for the axiom: \n", mb.goal())

    #does not entail
    if entail > 0:
        return False

    #does entail. create files for proofs
    else:
        if path:
            for c, proof in enumerate(saved_proofs):
                create_file("proof" + str(c + 1), proof, path)
        return True


# update owl files
def owl_update(t1, rel, t2, alt_file, meta_file):
    l1 = "ObjectPropertyAssertion(:" + rel
    l2 = " :" + t1 + " :" + t2 + ")\n\n"
    syntax1 = l1 + l2

    f = open(alt_file, "r")
    alt_lines = f.readlines()
    f.close()

    for c1 in range(len(alt_lines)-1, 0, -1):
        if alt_lines[c1] != "":
            alt_lines.insert(c1, syntax1)
            break

    f = open(alt_file, "w")
    alt_string = "".join(alt_lines)
    f.write(alt_string)
    f.close()

    l3 = "Declaration(NamedIndividual(:" + t1 + "))\n"

    l4 = "# Individual: :" + t1 + " (:" + t1 + ")\n\n"
    l5 = "ClassAssertion(:Theory :" + t1 + ")\n\n"

    l6 = "# Individual: :" + t2 + " (:" + t2 + ")\n\n"
    l7 = "ClassAssertion(:Theory :" + t2 + ")\n"

    l8 = "ObjectPropertyAssertion(:" + rel + " :" + t1 + " :" + t2 + ")\n\n"
    syntax2 = l4 + l5 + l6 + l7 + l8

    f = open(meta_file, "r")
    meta_lines = f.readlines()
    f.close()

    for c, l in enumerate(meta_lines):
        if l3 in l:
            break
        elif "###" in l:
            meta_lines.insert(c, l3)
            break
    for c1 in range(len(meta_lines)-1, 0, -1):
        if meta_lines[c1] != "":
            meta_lines.insert(c1, syntax2)
            break

    f = open(meta_file, "w")
    meta_string = "".join(meta_lines)
    f.write(meta_string)
    f.close()


def oracle(t1, lines_t1, t2, lines_t2, alt_file, meta_file, path=None):
    # consistent
    consistent = consistency(lines_t1, lines_t2, path)

    if consistent == "inconclusive":
        owl_update(t1, "inconclusive_", t2, alt_file, meta_file)
        #do we want to save any proofs for other axioms if it came out inconclusive?
        return "inconclusive_t1_t2"

    elif consistent:
        o1_entails_o2 = entailment(lines_t1, lines_t2, path)
        o2_entails_o1 = entailment(lines_t2, lines_t1, path)

        # consistent with inconclusive entailment
        #if only one is true, does that count as one-sided entailment???
        if o1_entails_o2 == "inconclusive" or o2_entails_o1 == "inconclusive":
            owl_update(t1, "consistent", t2, alt_file, meta_file)
            if path:
                os.rename(path, "consistent_" + t1 + "_" + t2)
            return "consistent_t1_t2"

        # equivalent
        if o1_entails_o2 & o2_entails_o1:
            if t1 != t2:
                owl_update(t1, "equivalent", t2, alt_file, meta_file)
                if path:
                    os.rename(path, "equivalent_" + t1 + "_" + t2)
            return "equivalent_t1_t2"

        # independent
        elif (o1_entails_o2 is False) & (o2_entails_o1 is False):
            owl_update(t1, "independent", t2, alt_file, meta_file)
            if path:
                os.rename(path, "independent_" + t1 + "_" + t2)
            return "independent_t1_t2"

        # t1 entails t2
        elif o1_entails_o2:
            owl_update(t1, "entails", t2, alt_file, meta_file)
            if path:
                os.rename(path, "entails_" + t1 + "_" + t2)
            return "entails_t1_t2"

        # t2 entails t1
        elif o2_entails_o1:
            owl_update(t2, "entails", t1, alt_file, meta_file)
            if path:
                os.rename(path, "entails_" + t2 + "_" + t1)
            return "entails_t2_t1"

    # inconsistent
    elif consistent is False:
        owl_update(t1, "inconsistent", t2, alt_file, meta_file)
        if path:
            os.rename(path, "inconsistent_" + t1 + "_" + t2)
        return "inconsistent_t1_t2"


def check(meta_file, t1, t2):
    # check if relationship has been found already
    possible = ["inconclusive",
                "consistent",
                "inconsistent",
                "entails",
                "independent",
                "equivalent"]

    with open(meta_file, "r") as file3:
        all_relations = file3.readlines()
        for r in all_relations:
            for p in possible:
                if "ObjectPropertyAssertion(:" + p + " :" + t1 + " :" + t2 + ")" in r:
                    # print("ObjectPropertyAssertion(:" + p + " :" + t1 + " :" + t2 + ")")
                    relationship = p + "_t1_t2"
                    file3.close()
                    return relationship
                elif "ObjectPropertyAssertion(:" + p + " :" + t2 + " :" + t1 + ")" in r:
                    # print("ObjectPropertyAssertion(:" + p + " :" + t2 + " :" + t1 + ")")
                    relationship = p + "_t2_t1"
                    file3.close()
                    return relationship
    file3.close()
    return "nf"


# main program
def main(t1, t2, file=False):

    t1 = t1.replace(".in", "")
    t2 = t2.replace(".in", "")

    alt_file = "alt-metatheory.owl"
    meta_file = "metatheory.owl"

    #check if relationship has been documented in owl file
    check_rel = check(meta_file, t1, t2)

    if check_rel == "nf":
        if file:
            new_dir = t1 + "_" + t2
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
        else:
            new_dir = None

        lines_t1 = theory_setup(t1 + ".in")
        lines_t2 = theory_setup(t2 + ".in")

        relationship = oracle(t1, lines_t1, t2, lines_t2, alt_file, meta_file, new_dir)
    else:
        relationship = check_rel

    return relationship


# t1 = input("enter theory 1:")
# t2 = input("enter theory 2:")
# print(main(t1, t2))
#print(main("branching.in", "upper_separative.in"))