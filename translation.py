'''
 August 2020
 By Amanda Chow
 This program extracts the p9 axioms from a .m4.out file
'''

import os


def extract_axioms(file_name):
    p9_axioms = []
    copy = False
    with open(file_name, "r") as f:
        for item in f:
            if "formulas(assumptions)" in item:
                copy = True
            if copy and "%" not in item:
                p9_axioms.append(item)
            if "end_of_list" in item:
                break
    return p9_axioms


def create_file(file_name):
    p9_axioms = extract_axioms(file_name)
    new_file = file_name.replace(".m4.out", ".in")
    with open(new_file, "w") as p9_file:
        p9_file.write("".join(p9_axioms))


def main(path):
    for file_name in os.listdir(path):
        if file_name.endswith(".m4.out"):
            create_file(path + "/" + file_name)


# def output_files(ontology):
#     os.chdir("cd Documents/GitHub/macleod/bin")
#     for file_name in os.listdir():
#         if file_name.endswith(".clif"):
#             os.system("python3 check_consistency_new.py -f /Users/amandachow/Documents/GitHub/colore/ontologies/"
#                       + ontology + "/" + file_name)


main("/Users/amandachow/PycharmProjects/research_2021/output_m4")
# output_files("between")
