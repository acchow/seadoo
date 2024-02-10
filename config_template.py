import os

# root directory containing all packages and files being used
# add and remove strings as needed. each "" contains the name of one folder, from top to bottom-most directory
path = os.path.join(os.path.sep, "", "", "")
hierarchy = os.path.join(os.path.sep, path, "", "")
hashemi = os.path.join(os.path.sep, path, "")

# owl files with existing relationships
alt = os.path.join(os.path.sep, hierarchy, "alt-metatheory.owl")
meta = os.path.join(os.path.sep, hierarchy, "metatheory.owl")

# parameters for computing theory relationships
create_files = False                                            # when True, proof files are generated for each relationship computation
definitions = os.path.join(os.path.sep, path, "definitions")    # directory containing definitions

# parameters relating to user models and search procedure
csv = os.path.join(os.path.sep, hierarchy, ".csv")                          # csv with chains
examples = os.path.join(os.path.sep, hashemi, "examples")                   # directory to examples
counterexamples = os.path.join(os.path.sep, hashemi, "counterexamples")     # directory to counterexamples
#translations = os.path.join(os.path.sep, path, "")                         # directory to translation definitions
answer_reports = os.path.join(os.path.sep, hashemi, "answer_reports")

# relationship for t1 and t2
t1 = ".in"
t2 = ".in"

# new theory for insertion
new_t = ".in"
function = 1    # 1 to insert, 2 to search for an equivalent theory to new_t

# database details
db = {
    'host': '',
    'schema': '', 
    'user': '', 
    'pw': '',
    'port': 3306
}

