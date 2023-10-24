# Semi-Automated Design of Ontologies
# Emily's branch
Used in conjunction with logical and mathematical theories (i.e., ontologies) found 
in the [Common Logic Ontology Repository (COLORE)](https://github.com/gruninger/colore). .
For further research and development, see the [SEADOO wiki](https://github.com/acchow/seadoo/wiki). 

## Setup
```
python3 -m venv venv                    //Create virtual environment
source venv/bin/activate                //Activate
pip install -r requirements.txt         //Install requirements
```

## Install theorem prover
[Prover9/Mace4 (LADR)](https://www.cs.unm.edu/~mccune/prover9/download/)
<br/>

## **hashemi**
Implementation of the Hashemi procedure. Constructs the closest matching theory to 
models provided by the user (consistent with all examples and inconsistent with all counterexamples)
using existing axioms from a *chain decomposition of theories. 
Generates additional models for user to classify as intended or unintended. Final answer containing
best matching axioms are generated in an answer report (.txt file). 

*chain decomposition: hierarchy of theories represented as linear chains, where one path from root to
leaf theory is equivalent to one chain

#### Files Required
1. Chain decomposition in a .csv file ([learn how to construct a new one](#insertion-and-hierarchy-construction))
2. Theory files containing respective axioms (in Prover9 syntax) for each theory listed in the 
chain decomposition
3. Model files in Mace4 'cooked' format, classified as examples and counterexamples (place examples
and counterexamples in separate directories)
4. Definition files for non-primitive relations used in 
the theories (use the relation signature as the file name)
5. Translation definition files that map relations in the models to 
relations in the theories (use the relation name in the models as the file name)

Important notes: 
* for #2-5, name all files with the suffix ".in"
* all axioms must be written in Prover9 syntax
* write all comments with a period at the end

#### Run hashemi procedure from /seadoo
```
mv ~/seadoo/hashemi/hashemi_config_template.py ~/seadoo/config.py       //Follow instructions for setup in config.py
python3 -m hashemi.search
```
<br/>

## **p9_tools**
Additional packages used for [hashemi](#hashemi). Can also be used independently as tools
for theories in Prover9 syntax. The [parse](https://github.com/acchow/seadoo/tree/master/p9_tools/parse) 
module is required for all other functionality. 

## **relationship**
Checks for consistency and finds the relationship between two theories. 
There are 6 different outcomes:
1. equivalent
2. one theory entails the other 
3. independent 
4. consistent 
5. inconsistent
6. inconclusive 

#### Run relationship from seadoo/
```
mv ~/seadoo/p9_tools/relationship/relationship_config_template.py ~/seadoo/config.py             //Follow instructions for setup in config.py
python3 -m p9_tools.relationship.relationship
```
<br/>

## **insertion**
There are 3 use cases for this package: 
1. Insert a theory into an existing chain decomposition (.csv file)
2. Search for an equivalent theory in an existing chain decomposition (.csv file)
3. Construct a new chain decomposition

### Use Case 1 and 2
#### Run insertion from seadoo/
```
mv ~/seadoo/p9_tools/insertion/insertion_config_template.py ~/seadoo/config.py    //Follow instructions for setup in config.py
python3 -m p9_tools.insertion.insertion
```

### Use Case 3
#### Run construct from seadoo/
```
mv ~/seadoo/p9_tools/insertion/insertion_config_template.py ~/seadoo/config.py    //Follow instructions for setup in config.py
touch <name_of_chain_decomp>.csv                                                  //Open this file and add a 0 as the first entry
python3 -m p9_tools.insertion.construct
```
<br><br/>