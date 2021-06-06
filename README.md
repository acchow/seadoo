# Semi-Automated Design of Ontologies
Used in conjunction with the [Common Logic Repository](https://github.com/gruninger/colore)

## Configurations
1. Enter all directory configurations into config.py
2. Install [NLTK](https://www.nltk.org/install.html)
3. Install [Prover9/Mace4 (LADR)](https://www.cs.unm.edu/~mccune/prover9/download/)

## Ontology relationships
Checks for consistency and finds the relationship between two ontologies

#### Run by command line
`python3 -m relationship.relationship`

## Insertion and Hierarchy Construction
Inserts a theory into a provided chain decomposition file in csv format, or searches for an equivalent theory to user input. 
The first row of the csv file must contain a list of integers from zero to the length of the longest existing chain. 
If this is an empty csv file (constructing a new hierarchy), enter the number 0 at the first position (row 0 column 0) before running 
the insertion. 

#### Additional Installations
1. [Pandas](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
2. relationship package

#### Run by command line
`python3 -m insertion.insertion`


## Search (Hashemi Procedure)

#### Additional Installations
1. [Pandas](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
2. relationship package

#### Run by command line
`python3 -m hashemi.search`


## Other tools
### Parser for translated P9 axioms
Extracts translated Prover9 axioms from .m4.out files generated into the output folder
by the [CLIF-P9 translator program on macleod](https://github.com/thahmann/macleod/wiki/macleod-python3-(beta)-GUI-setup) 

#### Run by command line
`python3 translation.py`
