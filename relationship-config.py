# template for directory configurations to find and prove the relationship between two theories
import os

# root directory containing all packages and files being used
# add and remove strings as needed. each "" contains the name of one folder, from top to bottom-most directory
path = os.path.join(os.path.sep, "", "", "")

# owl files with existing relationships
alt = os.path.join(os.path.sep, path, "alt-metatheory.owl")
meta = os.path.join(os.path.sep, path, "metatheory.owl")

# relationship between t1 and t2
t1 = ".in"
t2 = ".in"
create_files = False                                            # when True, proof files are generated
definitions = os.path.join(os.path.sep, path, "definitions")    # directory containing definitions


