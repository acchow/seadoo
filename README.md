# Semi-Automated Design of Ontologies
[seadoo wiki for developers ](https://github.com/acchow/seadoo/wiki)

Used in conjunction with ontologies in the [Common Logic Repository](https://github.com/gruninger/colore)

## Installations and Setup
1. [Python 3+](https://www.python.org/downloads/)
2. [NLTK](https://www.nltk.org/install.html)
3. [Prover9/Mace4 (LADR)](https://www.cs.unm.edu/~mccune/prover9/download/)
4. Create a Python file named config.py in the main directory containing all packages used
<br><br/>


## **Hashemi Procedure Implementation**
Finds the closest matching theories within a hierarchy, that are consistent with user example models and inconsistent
with user counterexample models

#### Additional Installations
1. [Pandas](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
2. relationship package

#### Files Required
1. Comma-separated values (.csv) file containing an existing hierarchy of ontologies, 
represented as linear chains (to construct a new hierarchy, see 
[hierarchy construction](#insertion-and-hierarchy-construction))
2. All ontology files listed in the chain decomposition from step 1 with axioms written 
in Prover9 syntax; all file names ending in ".in"
3. Example and counterexample models in Mace4 cooked format 
4. Definitions for all relations used in the hierarchy in Prover9 syntax 
5. Translation definitions that map relations found in user models to relations found in the theories contained
in the hierarchy 
6. Create a Python file and name it `config.py`

#### Paste the following into **config.py**
<pre><code># replace strings with your directory paths
create_files = False    
path = "/PATH/TO/ALL/PACKAGES/AND/FILES"                         
definitions = path + "/FOLDER/NAME/WITH/DEFINITIONS"    
csv = path + "/NAME/OF/CSV/FILE"   
examples = path + "/FOLDER/NAME/WITH/EXAMPLES"                 
counterexamples = path + "/FOLDER/NAME/WITH/COUNTEREXAMPLES"   
</code></pre>

#### Run by command line
Navigate to working directory, then run
`python3 -m hashemi.search`
<br><br/>

## **Other Ontology Tools**
Used for ontologies with axioms written in Prover9 syntax

### **Ontology Relationships**
Checks for consistency and finds the relationship between two ontologies

#### Run by command line
`python3 -m relationship.relationship`
<br><br/>

### **Insertion and Hierarchy Construction**
Inserts a theory into a provided chain decomposition file in csv format, or searches for an equivalent theory to user input. 
The first row of the csv file must contain a list of integers from zero to the length of the longest existing chain. 
If this is an empty csv file (constructing a new hierarchy), enter the number 0 at the first position (row 0, col 0) before running.

#### Additional Installations
1. [Pandas](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
2. relationship package

#### Run by command line
`python3 -m insertion.insertion`
<br><br/>

### Parser for translated P9 axioms
Extracts translated Prover9 axioms from .m4.out files generated into the output folder
by the [CLIF-P9 translator program on macleod](https://github.com/thahmann/macleod/wiki/macleod-python3-(beta)-GUI-setup) 

#### Run by command line
`python3 translation.py`

