from nltk import *
import timeout_decorator

import os.path
from os import path
import config

from p9_tools.relationship import files
from p9_tools.parse import theory

from nltk.sem import Expression
read_expr = Expression.fromstring

CREATE_FILES = config.create_files
FILE_PATH = config.hierarchy
DEFINITIONS_PATH = config.definitions
ALT_FILE = config.alt
META_FILE = config.meta


@timeout_decorator.timeout(30)
def build_model(mb: MaceCommand): 
    return mb.build_model()


def consistency(lines_t1, lines_t2, new_dir):
    lines = lines_t1 + lines_t2
    assumptions = read_expr(lines[0])

    # look for 10 models before timeout
    mb = MaceCommand(None, [assumptions], max_models=10)
    for c, added in enumerate(lines[1:]):
        mb.add_assumptions([read_expr(added)])

    # use mb.build_model([assumptions]) to print the input
    consistent = "inconclusive"
    model = False
    try:
        model = build_model(mb)
        # found a model, the theories are consistent with each other
        if model:
            consistent = True
            consistent_model = mb.model(format='cooked')
            if new_dir:
                files.create_file(new_dir, "consistent_model", consistent_model)

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
                if new_dir:
                    files.create_file(new_dir, "inconsistent_proof", inconsistent_proof)
            else:
                consistent = "inconclusive"
        except Exception:  # proof timeout, reached max time limit
            consistent = "inconclusive"  # no model and no proof, inconclusive relationship

    return consistent


def entailment(lines_t1, lines_t2, new_dir):
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
                #counterexample = mb.build_model()
                counterexample = False
                counterexample = build_model(mb)

                # counterexample found. does not entail. create file for counterexample
                if counterexample & (counter_file_created is False):
                    counterexample_model = mb.model(format='cooked')
                    if new_dir:
                        files.create_file(new_dir, "counterexample_found", counterexample_model)
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
        if new_dir:
            for c, proof in enumerate(saved_proofs):
                files.create_file(new_dir, "proof" + str(c + 1), proof)
        return True


def oracle(t1_file, t2_file, lines_t1, lines_t2, new_dir):
    rel = ""
    t1 = t1_file.replace(".in", "")
    t2 = t2_file.replace(".in", "")

    # consistent
    consistent = consistency(lines_t1, lines_t2, new_dir)

    if consistent == "inconclusive":
        files.owl("inconclusive")
        if new_dir:
            files.delete_dir(os.path.join(FILE_PATH, new_dir))
        rel = "inconclusive_t1_t2"

    elif consistent:
        t1_entails_t2 = entailment(lines_t1, lines_t2, new_dir)
        t2_entails_t1 = entailment(lines_t2, lines_t1, new_dir)

        # consistent with inconclusive entailment
        # if either side entailment is inconclusive, the relationship is deemed inconclusive (consistent only)
        if t1_entails_t2 == "inconclusive" or t2_entails_t1 == "inconclusive":
            files.owl("consistent")
            files.rename_dir("consistent", new_dir, t1, t2)
            rel = "consistent_t1_t2"

        # equivalent
        elif t1_entails_t2 & t2_entails_t1:
            if t1 != t2:
                files.owl("equivalent")
                files.rename_dir("equivalent", new_dir, t1, t2)
            rel = "equivalent_t1_t2"

        # independent
        elif (t1_entails_t2 is False) & (t2_entails_t1 is False):
            files.owl("independent")
            files.rename_dir("independent", new_dir, t1, t2)
            rel = "independent_t1_t2"

        # t1 entails t2
        elif t1_entails_t2:
            files.owl("entails")
            files.rename_dir("entails", new_dir, t1, t2)
            rel = "entails_t1_t2"

        # t2 entails t1
        elif t2_entails_t1:
            files.owl("entails", t2, t1)
            files.rename_dir("entails", new_dir, t2, t1)
            rel = "entails_t2_t1"

    # inconsistent
    elif consistent is False:
        files.owl("inconsistent")
        files.rename_dir("inconsistent", new_dir, t1, t2)
        rel = "inconsistent_t1_t2"

    return rel


# main program
def main(t1_file=config.t1, t2_file=config.t2):
    # check if relationship has been documented in owl file
    check_rel = files.check()

    check_rel = "nf"

    # nf = relationship not found in the file
    if check_rel == "nf":
        t1 = t1_file.replace(".in", "")
        t2 = t2_file.replace(".in", "")

        # create directory with proof and model files
        if CREATE_FILES:
            # check if directory exists
            exists = False
            possibilities = ["consistent", "inconsistent", "equivalent", "independent", "entails"]

            for rel in possibilities:
                dir_12 = rel + "_" + t1 + "_" + t2
                dir_21 = rel + "_" + t2 + "_" + t1
                if os.path.isdir(os.path.join(FILE_PATH, dir_12)) or os.path.isdir(os.path.join(FILE_PATH, dir_21)):
                    print("directory name", dir_12, "or", dir_21, "already exists. cannot create directory with "
                                                                  "proofs and models unless renamed.")
                    exists = True
                    break

            # create directory
            if not exists:
                try:
                    new_dir = t1 + "_" + t2
                    os.mkdir(os.path.join(FILE_PATH, new_dir))
                except OSError:
                    print("directory name", new_dir, "already exists. cannot create directory with proofs and "
                                                     "models unless renamed.")
                    new_dir = ""
            else:
                new_dir = ""

        else:
            new_dir = ""

        lines_t1 = theory.theory_setup(os.path.join(FILE_PATH, t1_file))
        lines_t2 = theory.theory_setup(os.path.join(FILE_PATH, t2_file))

        relationship = ""
        if lines_t1 and lines_t2: 
            if not path.exists(DEFINITIONS_PATH):
                print("definitions directory ", DEFINITIONS_PATH, " not found")
            else:
                relationship = oracle(t1_file, t2_file, lines_t1, lines_t2, new_dir)
    else:
        relationship = check_rel

    return relationship


if __name__ == "__main__":
    print(main())
