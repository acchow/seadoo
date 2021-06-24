import os
from p9_tools import config

T1 = config.t1
T2 = config.t2
FILE_PATH = config.path
ALT_FILE = config.alt
META_FILE = config.meta


def create_file(new_dir, name, contents):
    new_path = os.path.join(FILE_PATH, new_dir, name)
    with open(new_path, "w+") as new_file:
        new_file.write(contents)


def delete_dir(file_path):
    for file in os.listdir(file_path):
        os.remove(file)
    os.rmdir(file_path)


def rename_dir(rel, new_dir, t1, t2):
    if new_dir:
        new_name = rel + "_" + t1 + "_" + t2
        new_path = os.path.join(FILE_PATH, new_dir)
        os.rename(new_path, new_name)


# update owl files
def owl(rel, t1=T1, t2=T2):
    l1 = "ObjectPropertyAssertion(:" + rel
    l2 = " :" + t1 + " :" + t2 + ")\n\n"
    syntax1 = l1 + l2

    f = open(ALT_FILE, "r")
    alt_lines = f.readlines()
    f.close()

    for c1 in range(len(alt_lines)-1, 0, -1):
        if alt_lines[c1] != "":
            alt_lines.insert(c1, syntax1)
            break

    f = open(ALT_FILE, "w")
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

    f = open(META_FILE, "r")
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

    f = open(META_FILE, "w")
    meta_string = "".join(meta_lines)
    f.write(meta_string)
    f.close()


def check():
    t1 = T1.replace(".in", "")
    t2 = T2.replace(".in", "")

    # check if relationship has been found already
    possible = ["inconclusive",
                "consistent",
                "inconsistent",
                "entails",
                "independent",
                "equivalent"]

    with open(META_FILE, "r") as file3:
        all_relations = file3.readlines()
        for r in all_relations:
            for p in possible:
                if "ObjectPropertyAssertion(:" + p + " :" + t1 + " :" + t2 + ")" in r:
                    relationship = p + "_t1_t2"
                    file3.close()
                    return relationship
                elif "ObjectPropertyAssertion(:" + p + " :" + t2 + " :" + t1 + ")" in r:
                    relationship = p + "_t2_t1"
                    file3.close()
                    return relationship
    file3.close()
    # nf = not found
    return "nf"


