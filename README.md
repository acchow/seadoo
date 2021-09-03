# Semi-Automated Design of Ontologies

Used in conjunction with logical and mathematical theories (i.e., ontologies) found 
in the [Common Logic Ontology Repository](https://github.com/gruninger/colore). For 
further research and development, see the 
[SEADOO wiki](https://github.com/acchow/seadoo/wiki). 

#### Installations
1. [Python 3+](https://www.python.org/downloads/)
2. [NLTK](https://www.nltk.org/install.html)
3. [Prover9/Mace4 (LADR)](https://www.cs.unm.edu/~mccune/prover9/download/)
4. [Pandas](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
<br><br/>

## **hashemi**
Implementation of the Hashemi procedure. Constructs the closest matching theory to 
models provided by the user (consistent with all examples and inconsistent with all counterexamples)
using existing axioms from a *chain decomposition of theories. 
Generates additional models for user to classify as intended or unintended. Final answer containing
best matching axioms are generated in an answer report (.txt file). 

*chain decomposition: hierarchy of theories represented as linear chains, where one path from root to
leaf theory is equivalent to one chain

#### Files Required
1. Chain decomposition in a .csv file ([construct a new one](#insertion-and-hierarchy-construction))
2. Theory files containing respective axioms (in Prover9 syntax) for each theory listed in the 
chain decomposition
3. Model files in Mace4 'cooked' format, classified as examples and counterexamples (place examples
and counterexamples in separate directories)
4. Definition files for non-primitive relations used in 
the theories (use the relation signature as the file name)
5. Translation definition files that map relations in the models to 
relations in the theories (use the relation name in the models as the file name)

Notes: 
* for #2-5, name all files with the suffix ".in"
* all axioms must be written in Prover9 syntax

#### Directory configurations
1. Open the [hashemi config template](https://github.com/acchow/seadoo/blob/master/hashemi/hashemi-config-template.py)
and follow instructions to specify your directory paths for theories, models, etc. 
2. Rename the file to `config.py`
3. Place it in the root directory 

#### Run by command line
Navigate to working directory, then run
`python3 -m hashemi.search`
<br><br/>

## **p9_tools**
Additional packages used for [hashemi](#hashemi). Can also be used independently as tools
for theories in Prover9 syntax. The [parse](https://github.com/acchow/seadoo/tree/master/p9_tools/parse) 
module is required for all other functionality. 

## **relationship**
Checks for consistency and finds the relationship between two theories. 
There are 6 different outcomes:
1. equivalent
2. one theory entails another 
3. independent 
4. consistent 
5. inconsistent
6. inconclusive 

#### Directory configurations
1. Open the [relationship config template](https://github.com/acchow/seadoo/blob/master/p9_tools/relationship-config-template.py)
and follow instructions to specify your directory paths. 
2. Rename the file to `config.py`
3. Place it in the root directory 

#### Run by command line
Navigate to working directory, then run `python3 -m p9_tools.relationship.relationship`
<br><br/>

## **insertion**
There are 3 use cases for this package: 
1. Insert a theory into an existing chain decomposition
2. Search for an equivalent theory in an existing chain decomposition
3. Construct a new chain decomposition 

#### Directory configurations
1. Open the [insertion config template](https://github.com/acchow/seadoo/blob/master/p9_tools/insertion-config-template.py)
and follow instructions to specify your use case and directory paths. 
2. Rename the file to `config.py`
3. Place it in the root directory 

### Use Case 1 and 2
#### Run by command line
Navigate to working directory, then run `python3 -m p9_tools.insertion.insertion`
<br><br/>

### Use Case 3
#### Run by command line
Navigate to working directory, then run `python3 -m p9_tools.insertion.construct`
<br><br/>