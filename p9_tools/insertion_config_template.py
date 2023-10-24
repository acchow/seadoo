# template for directory configurations to insert a new theory or create a new chain decomposition
import os

# root directory containing all packages and files being used
# when constructing new hierarchy, place all theories in this directory
# add and remove strings as needed. each "" contains the name of one folder, from top to bottom-most directory
path = os.path.join(os.path.sep, "", "", "")

# owl files with existing relationships
alt = os.path.join(os.path.sep, path, "alt-metatheory.owl")
meta = os.path.join(os.path.sep, path, "metatheory.owl")

# relationship between t1 and t2
create_files = False                           # when True, proof files are generated for each relationship computation
definitions = os.path.join(os.path.sep, path, "definitions")    # directory containing definition files

# parameters for insertion
new_t = "new-theory-name.in"                        # name of new theory input file
csv = os.path.join(os.path.sep, path, ".csv")       # csv with chains or where new chains will be constructed
function = 1                                        # 1 to insert, 2 to search for an equivalent theory to new_t

t1 = ".in"
t2 = ".in"