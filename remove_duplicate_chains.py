
#remove duplicate chains in chain decomposition

def duplicate_check(short, long):
    # check if two chains are duplicates
    # duplicate = if one chain is subset of another

    #index of theory being checked in the shorter chain
    i = 0

    #check if each theory in short chain exists in long
    for t in long:
        if t == short[i]:
            i+=1
            #reached end of short chain, all theories in short found in long
            if i == len(short):
                #they are duplicates
                return True

    return False



def remove(chains_list):

    #chain # being checked against all other chains
    #chain "x"
    for i, x in enumerate(chains_list):

        #all other chains
        for c in (chains_list[:i] + chains_list[i+1:]):
            # assign a short and long chain
            if len(x) <= len(c):
                short = x
                long = c
            else:
                short = c
                long = x

            if duplicate_check(short, long):
                chains_list.remove(short)













