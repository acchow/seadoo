import os
'''
GENERAL INSTRUCTIONS:
- Add and remove quotations as needed, separated by commas, in each os.path.join( ... )
- Each quotation should contain the name of ONE directory, from the top to bottom-most directories  
- Enter directory names where it says <FILL> 
- Directory and file names that are already specified in quotations should be created as new folders if they do not exist already
'''


'''
REQUIRED FOR ALL OF seadoo:
- path: The directory where seadoo is located 
- repo: Where the theory files are located. Each subdirectory name should match what is found in colore/ontologies/
'''
path = os.path.join(os.path.sep, '<FILL>', 'seadoo')
repo = os.path.join(os.path.sep, path, '<FILL>', 'ontologies')


'''
USED FOR seadoo/search MODULE:
- search: Search path
- hierarchy: Directory name of the known hierarchy that is under seadoo/ontologies/. Required only for search.hashemi
- examples, counterexamples, answer_reports, translations: Create these directories under seadoo/
- alt, meta: Create these files under each hierarchy under seadoo/ontologies/<hierarchy_name>/
- db: Database details. Required only for search.modular_ontology
'''
search = os.path.join(os.path.sep, path, 'search')
hierarchy = '<FILL>'
examples = os.path.join(os.path.sep, search, 'examples')
counterexamples = os.path.join(os.path.sep, search, 'counterexamples')
answer_reports = os.path.join(os.path.sep, search, 'answer_reports')
translations = os.path.join(os.path.sep, path, 'translations')
alt = os.path.join(os.path.sep, repo, hierarchy, 'alt-metatheory.owl')
meta = os.path.join(os.path.sep, repo, hierarchy, 'metatheory.owl')
db = {
    'host': '<FILL>',
    'schema': '<FILL>', 
    'user': '<FILL>', 
    'pw': '<FILL>',
    'port': 0,
}


'''
USED FOR seadoo/relationship MODULE
- definitions: Create this directory under seadoo/
- create_files: Flag to generate proof files for each computation. False by default
- t1, t2: Names of two theories being checked 
'''
definitions = os.path.join(os.path.sep, path, 'definitions')
create_files = False
t1 = '<FILL>'
t2 = '<FILL>'


'''
USED FOR seadoo/insertion MODULE
- new_t: a new theory to be inserted into an existing hierarchy e.g., quasi_order.in
- function: 1 to insert a new theory, 2 to find the equivalent theory to new_t. 1 by default
'''
new_t = '<FILL>'
function = 1

