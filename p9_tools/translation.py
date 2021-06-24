import os
from p9_tools import config

FILE_PATH = config.path


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


def main():
    for file_name in os.listdir(FILE_PATH):
        if file_name.endswith(".m4.out"):
            create_file(os.path.join(FILE_PATH, file_name))


if __name__ == "__main__":
    main()
