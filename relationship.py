from nltk import *
import parser
import files

from nltk.sem import Expression
read_expr = Expression.fromstring


def consistency(lines_t1, lines_t2, path=None):
    lines = lines_t1 + lines_t2
    assumptions = read_expr(lines[0])

    # look for 1 model before timeout
    mb = MaceCommand(None, [assumptions], max_models=10)
    for c, added in enumerate(lines[1:]):
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
                files.create_file("consistent_model", consistent_model, path)

    except Exception:
        consistent = "inconclusive"  # inconclusive results so far, no model found

    # no model exists, or Mace reached max number of models
    if model is False:
        prover = Prover9Command(None, [assumptions], timeout=30)
        for c, added in enumerate(lines[1:]):
            prover.add_assumptions([read_expr(added)])

        # try to find a proof for inconsistency
        try:
            proven = prover.prove()
            # proof found, result is inconsistent
            if proven:
                consistent = False
                inconsistent_proof = prover.proof()
                if path:
                    files.create_file("inconsistent_proof", inconsistent_proof, path)
            else:
                consistent = "inconclusive"
        except Exception:  # proof timeout, reached max time limit
            consistent = "inconclusive"  # no model and no proof, inconclusive relationship

    return consistent


def entailment(lines_t1, lines_t2, path=None):
    saved_proofs = []
    entail = 0
    counter_file_created = False

    for c1, goal in enumerate(lines_t2):
        # set first lines to use prover
        assumptions = read_expr(lines_t1[0])
        goals = read_expr(goal)

        prover = Prover9Command(goals, [assumptions], timeout=30)

        # add axioms into assumptions
        for c, added in enumerate(lines_t1[1:]):
            prover.add_assumptions([read_expr(added)])

        # print("from prover9, assumptions: \n", prover.assumptions())
        # print("from p9, the goal: \n", prover.goal())

        proven = False
        proof_timeout = False
        # find proof of entailment for this axiom
        try:
            proven = prover.prove()
            if proven & (entail == 0):
                get_proof = prover.proof()
                saved_proofs.append(get_proof)
        except Exception:  # proof timeout, reached max time limit
            proof_timeout = True

        if proven is False:
            entail += 1
            # saved_proofs.clear()

            mb = MaceCommand(goals, [assumptions], max_models=10)
            for c, added in enumerate(lines_t1[1:]):
                mb.add_assumptions([read_expr(added)])

            # print("from mace, assumptions: \n", mb.assumptions())
            # print("from mace, the goal: \n", mb.goal())

            # use mb.build_model([assumptions]) to print the input
            try:
                counterexample = mb.build_model()

                # counterexample found. does not entail. create file for counterexample
                if counterexample & (counter_file_created is False):
                    counterexample_model = mb.model(format='cooked')
                    if path:
                        files.create_file("counterexample_found", counterexample_model, path)
                    counter_file_created = True

            except Exception:
                counterexample = False

            # new_axioms.append(mb.goal())

            # counterexample not found and no proof (dne or timed out), inconclusive results
            if counterexample is False and (proven is False or proof_timeout):
                return "inconclusive"

            # elif counterexample is False:
            #     print("no counterexample found for the axiom: \n", mb.goal())

    # does not entail
    if entail > 0:
        return False

    # does entail. create files for proofs
    else:
        if path:
            for c, proof in enumerate(saved_proofs):
                files.create_file("proof" + str(c + 1), proof, path)
        return True


def oracle(t1, lines_t1, t2, lines_t2, alt_file, meta_file, path=None):
    # consistent
    consistent = consistency(lines_t1, lines_t2, path)

    if consistent == "inconclusive":
        files.owl(t1, "inconclusive_", t2, alt_file, meta_file)
        # do we want to save any proofs for other axioms if it came out inconclusive?
        # log it back to the ontology designer
        return "inconclusive_t1_t2"

    elif consistent:
        o1_entails_o2 = entailment(lines_t1, lines_t2, path)
        o2_entails_o1 = entailment(lines_t2, lines_t1, path)

        # consistent with inconclusive entailment
        # if either result is inconclusive, the whole relationship is deemed inconclusive (consistent only)
        if o1_entails_o2 == "inconclusive" or o2_entails_o1 == "inconclusive":
            files.owl(t1, "consistent", t2, alt_file, meta_file)
            if path:
                os.rename(path, "consistent_" + t1 + "_" + t2)
            return "consistent_t1_t2"

        # equivalent
        if o1_entails_o2 & o2_entails_o1:
            if t1 != t2:
                files.owl(t1, "equivalent", t2, alt_file, meta_file)
                if path:
                    os.rename(path, "equivalent_" + t1 + "_" + t2)
            return "equivalent_t1_t2"

        # independent
        elif (o1_entails_o2 is False) & (o2_entails_o1 is False):
            files.owl(t1, "independent", t2, alt_file, meta_file)
            if path:
                os.rename(path, "independent_" + t1 + "_" + t2)
            return "independent_t1_t2"

        # t1 entails t2
        elif o1_entails_o2:
            files.owl(t1, "entails", t2, alt_file, meta_file)
            if path:
                os.rename(path, "entails_" + t1 + "_" + t2)
            return "entails_t1_t2"

        # t2 entails t1
        elif o2_entails_o1:
            files.owl(t2, "entails", t1, alt_file, meta_file)
            if path:
                os.rename(path, "entails_" + t2 + "_" + t1)
            return "entails_t2_t1"

    # inconsistent
    elif consistent is False:
        files.owl(t1, "inconsistent", t2, alt_file, meta_file)
        if path:
            os.rename(path, "inconsistent_" + t1 + "_" + t2)
        return "inconsistent_t1_t2"


# main program
def main(t1, t2, file=False):
    t1 = t1.replace(".in", "")
    t2 = t2.replace(".in", "")

    alt_file = "alt-metatheory.owl"
    meta_file = "metatheory.owl"

    # check if relationship has been documented in owl file
    check_rel = files.check(meta_file, t1, t2)

    #check_rel = "nf"

    # nf = relationship not found in the file
    if check_rel == "nf":
        if file:
            new_dir = t1 + "_" + t2
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
        else:
            new_dir = None

        lines_t1 = parser.theory_setup(t1 + ".in")
        lines_t2 = parser.theory_setup(t2 + ".in")

        #print("t1: ", parser.signatures(lines_t1))
        #print("t2: ", parser.signatures(lines_t2))

        relationship = oracle(t1, lines_t1, t2, lines_t2, alt_file, meta_file, new_dir)
    else:
        relationship = check_rel

    return relationship

# t1 = input("enter theory 1:")
# t2 = input("enter theory 2:")
# print(main(t1, t2))
print(main("up_branch.in", "upper_separative.in"))
