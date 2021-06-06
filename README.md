# The Oracle
(last updated 08/2020) 
This project includes scripts used as tools for the [Common Logic Repository](https://github.com/gruninger/colore) to navigate its ontologies through insertion and search algorithms.

## relationship.py (“the oracle”)
(previously named consistent.py)

This program finds the relationship between two theories using Prover9 and Mace. There are 5 possible outcomes: theories are inconsistent, theories are independent, theory 1 entails theory 2, theory 2 entails theory 1, or theories are equivalent. 

#### Installations Required
NLTK: https://www.nltk.org/install.html

Prover9/Mace4 (LADR): https://www.cs.unm.edu/~mccune/prover9/download/

#### Instructions
1. Open the script using a python IDE and scroll to the bottom line of code
2. Enter two parameters in main(,) with file names of two Prover9 theories ending in .in (order does not matter)
3. Parameter 1 is considered “theory 1” and parameter 2 is “theory 2”
4. Save all and run the program
5. Program will print one of five answers
   - equivalent_t1_t2 → theory 1 and theory 2 are equivalent (commutative)
   - independent_t1_t2 → theory 1 and theory 2 are independent (commutative)
   - entails_t1_t2 → theory 1 entails theory 2
   - entails_t2_t1 → theory 2 entails theory 1
   - inconsistent_t1_t2 → theory 1 and theory 2 are inconsistent (commutative)
6. File will be generated with all corresponding models and proofs under name “relationship”_”theoryname”_”theoryname” (i.e. entails_linearity_betweenness)


## insertion.py 
This program inserts a theory into a provided chain decomposition file in csv format. The first row of the csv file must contain a list of integers from zero to the length of the longest existing chain. If this is an empty csv file, enter the number 0 at the first position (row 0 column 0) before running the insertion. All subsequent rows are individual chains from the ontology, in no particular order. This script can also search for an equivalent theory. 

#### Installations Required
NLTK: https://www.nltk.org/install.html

Prover9/Mace4 (LADR): https://www.cs.unm.edu/~mccune/prover9/download/

Pandas: https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html

relationship.py

#### Instructions
1. Open the script using a python IDE and scroll to the bottom line of code
2. Enter three parameters in main(,,): (1) name of csv file containing chain decomposition ending in .csv, (2) name of proposed theory for insertion or search ending in .in, and (3) integer 1 to conduct an insertion or integer 2 to conduct a search
3. Save all and run the program
4. For insertion, check the csv file for updated chains. For search, the program will print the name of an equivalent theory found, or the message “no equivalent theory found”.
5. For insertion, files will be created for each comparison made to other theories


## search.py
This program accepts a user’s model and finds the closest matching theories from the chain decomposition. 

#### Installations Required
NLTK: https://www.nltk.org/install.html

Prover9/Mace4 (LADR): https://www.cs.unm.edu/~mccune/prover9/download/

Pandas: https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html

relationship.py

#### Instructions
1. Open the script using a python IDE and scroll to the bottom line of code
2. Enter two parameters in main(,): (1) name of csv file containing chain decomposition ending in .csv, (2) name of model proposed ending in .in
3. Save all and run the program
4. Program will print a list of all closest matching theories from each list in the same order as which chains appear in csv file


## translation.py
This program extracts translated Prover9 axioms from every file in its corresponding directory ending in .m4.out. The .m4.out files are created by the [CLIF-P9 translator program on macleod](https://github.com/thahmann/macleod/wiki/macleod-python3-(beta)-GUI-setup) and generated into a file called “output”. 

#### No Installations Required

#### Instructions
1. Open the script using a python IDE
2. Run the program
3. All Prover9 input files ending in .in will be generated in the same folder
