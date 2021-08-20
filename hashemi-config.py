# template for directory configurations to run the hashemi procedure
import os

# root directory containing all packages and files being used
# add and remove strings as needed. each "" contains the name of one folder, from top to bottom-most directory
path = os.path.join(os.path.sep, "", "", "")

# owl files with existing relationships
alt = os.path.join(os.path.sep, path, "alt-metatheory.owl")
meta = os.path.join(os.path.sep, path, "metatheory.owl")

# parameters for computing theory relationships
create_files = False                           # when True, proof files are generated for each relationship computation
definitions = os.path.join(os.path.sep, path, "definitions")    # directory containing definitions

# parameters relating to user models and search procedure
csv = os.path.join(os.path.sep, path, ".csv")                   # csv with chains
examples = os.path.join(os.path.sep, path, "")                  # directory to examples
counterexamples = os.path.join(os.path.sep, path, "")           # directory to counterexamples
translations = os.path.join(os.path.sep, path, "")              # directory to translation definitions
