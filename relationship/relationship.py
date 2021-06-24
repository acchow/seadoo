from nltk import *

import os.path
from os import path
import config       # contains all specified file paths

from relationship import files
from parse import theory

from nltk.sem import Expression
read_expr = Expression.fromstring

T1 = config.t1
T2 = config.t2
FILE_PATH = config.path
DEFINITIONS_PATH = config.definitions
ALT_FILE = config.alt
META_FILE = config.meta


def consistency(lines_t1, lines_t2):
    lines = lines_t1 + lines_t2
    assumptions = read_expr(lines[0])

    # look for 10 models before timeout
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
            if FILE_PATH:
                files.create_file("consistent_model", consistent_model)

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
                if FILE_PATH:
                    files.create_file("inconsistent_proof", inconsistent_proof)
            else:
                consistent = "inconclusive"
        except Exception:  # proof timeout, reached max time limit
            consistent = "inconclusive"  # no model and no proof, inconclusive relationship

    return consistent


def entailment(lines_t1, lines_t2):
    saved_proofs = []
    entail = 0
    counter_file_created = False

    signatures = theory.signatures(lines_t2)
    for s in signatures:
        # add t2 (goal) definitions to t1 (assumptions)
        # does not check if they exist in lines_t1 already; may encounter duplicates
        lines_t1 += theory.definitions(s)

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
                    if FILE_PATH:
                        files.create_file("counterexample_found", counterexample_model)
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
        if FILE_PATH:
            for c, proof in enumerate(saved_proofs):
                files.create_file("proof" + str(c + 1), proof)
        return True


def oracle(lines_t1, lines_t2, new_dir):
    # consistent
    consistent = consistency(lines_t1, lines_t2)

    if consistent == "inconclusive":
        files.owl("inconclusive")
        os.remove(FILE_PATH, T1 + "_" + T2)
        return "inconclusive_t1_t2"

    elif consistent:
        t1_entails_t2 = entailment(lines_t1, lines_t2)
        t2_entails_t1 = entailment(lines_t2, lines_t1)

        # consistent with inconclusive entailment
        # if either side entailment is inconclusive, the relationship is deemed inconclusive (consistent only)
        if t1_entails_t2 == "inconclusive" or t2_entails_t1 == "inconclusive":
            files.owl("consistent")
            if new_dir:
                os.rename(FILE_PATH, "consistent_" + T1 + "_" + T2)
            return "consistent_t1_t2"

        # equivalent
        elif t1_entails_t2 & t2_entails_t1:
            if T1 != T2:
                files.owl("equivalent")
                if new_dir:
                    os.rename(FILE_PATH, "equivalent_" + T1 + "_" + T2)
            return "equivalent_t1_t2"

        # independent
        elif (t1_entails_t2 is False) & (t2_entails_t1 is False):
            files.owl("independent")
            if new_dir:
                os.rename(FILE_PATH, "independent_" + T1 + "_" + T2)
            return "independent_t1_t2"

        # t1 entails t2
        elif t1_entails_t2:
            files.owl("entails")
            if new_dir:
                os.rename(FILE_PATH, "entails_" + T1 + "_" + T2)
            return "entails_t1_t2"

        # t2 entails t1
        elif t2_entails_t1:
            files.owl("entails", T2, T1)
            if new_dir:
                os.rename(FILE_PATH, "entails_" + T2 + "_" + T1)
            return "entails_t2_t1"

    # inconsistent
    elif consistent is False:
        files.owl("inconsistent")
        if new_dir:
            os.rename(FILE_PATH, "inconsistent_" + T1 + "_" + T2)
        return "inconsistent_t1_t2"


# main program
def main(file=False):
    # check if relationship has been documented in owl file
    check_rel = files.check()

    # check_rel = "nf"

    # nf = relationship not found in the file
    if check_rel == "nf":
        # create directory with proof and model files
        if file:
            try:
                new_dir = T1.replace(".in", "") + "_" + T2.replace(".in", "")
                os.mkdir(new_dir)
            except OSError:     # directory already exists
                new_dir = None

        else:
            new_dir = None

        lines_t1 = theory.theory_setup(os.path.join(FILE_PATH, T1))
        lines_t2 = theory.theory_setup(os.path.join(FILE_PATH, T2))

        if not path.exists(DEFINITIONS_PATH):
            print("definitions directory ", DEFINITIONS_PATH, " not found")
            relationship = "relationship cannot be found"
        else:
            relationship = oracle(lines_t1, lines_t2, new_dir)
    else:
        relationship = check_rel

    return relationship


if __name__ == "__main__":
    # print(main())
    main()

