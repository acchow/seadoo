import os
import config
from p9_tools.insertion import insertion

FILE_PATH = config.path


# construction of a hierarchy
def construct_hierarchy():
    for file_name in os.listdir(FILE_PATH):
        if file_name.endswith(".in"):
            insertion.main(file_name, True)


construct_hierarchy()
