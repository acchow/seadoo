from search.hashemi import *
import itertools


def get_hierarchies_by_type(num_relations): 
    conn = None
    try: 
        conn = mysql.connector.connect(
            host=config.db['host'], 
            database=config.db['schema'],
            user=config.db['user'],
            password=config.db['pw'], 
            port=config.db['port']
        )
    except Error as e: 
        print('Error connecting to database', config.db['schema'], e)
        return False
    
    cursor = conn.cursor()
    query_cols = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{}' AND TABLE_NAME = '{}'".format(config.db['schema'], 'hierarchies')
    cursor.execute(query_cols)
    cols = [row for row in cursor]
    
    q = "SELECT * FROM hierarchies WHERE num_prim_relations = {}".format(num_relations)
    cursor.execute(q)
    hierarchies = [row for row in cursor]

    info = []
    for row in hierarchies: 
        temp = {}
        for i in range(len(row)): 
            temp[cols[i][0]] = row[i]
        info.append(temp)
    # print(info)
    return info


def nondecomp(): 
    #generalize
    nd = get_hierarchies_by_type(1)   # 1 relation for nondecomp 
    nd_map = {}                       # key is model signature, value is dict with info 

    # get signatures and respective axioms from examples 
    for ex_file in os.listdir(EX_PATH):
        if ex_file.endswith(".in"):
            model_lines = model.model_setup(os.path.join(EX_PATH, ex_file), closed_world=True)
            temp = extract_signatures(model_lines)
            nd_map.update(temp)

    # compare the axioms for each signature with every root theory 
    for key in nd_map: 
        print('\nfinding nondecomposable hierarchy match for', key, 'relation signature...')
        nd_map[key]['nd'] = []
        for hier in nd:
            # get root theory
            if not hier['root_theory']: 
                print('root theory for', hier['hierarchy_name'], 'hierarchy not specified in database. skipping...')
                continue
            rt_name = hier['root_theory'] + '.in'   
            rt_path = os.path.join(os.path.sep, REPO_PATH, hier['hierarchy_name'], rt_name)
            if not os.path.isfile(rt_path): 
                print('root theory', rt_name, 'not found in', rt_path, '. skipping...')
                continue
            
            # consistency check with examples 
            rt_lines = theory.theory_setup(rt_path)
            consistent = True
            if not relationship.consistency(nd_map[key]['axioms'], rt_lines, new_dir=""): 
                consistent = False
            if consistent: 
                nd_map[key]['nd'].append(hier['hierarchy_name'])
        
        if not nd_map[key]['nd']: 
            print('inconsistent with all nd hierarchies')
        else: 
            print(key,'is consistent with', nd_map[key]['nd'])
    return nd_map


def get_trunk_theories(hier: str) -> list: 
    trunk_theory_list = []
    path = os.path.join(os.path.sep, REPO_PATH, hier, hier + ".csv")
    try:
        trunk_df = pd.read_csv(path, usecols=[1]).values.tolist()
    except FileNotFoundError: 
        print(path, 'chain decomposition not found. unable to search.')
        return False
    except pd.errors.EmptyDataError: 
        print(path, 'chain decomposition is empty. unable to search.')
        return False
    trunk_df = [t for t in trunk_df if list(filter(lambda a: pd.notna(a), t))]
    trunk_theory_list = list(set(str(s)[2:-2] + ".in" for s in trunk_df))
    return trunk_theory_list


def get_theory_pairs(theories: list) -> list:
    check = {}
    if len(theories) >= 2: 
        pairs = list(itertools.combinations(list(set(theories)),2))
        for t in theories: 
            if t not in check: 
                check[t] = 1
            else: 
                check[t] += 1
        for t in check: 
            if check[t] >= 1: 
                pairs.append((t,t))         #for reducible hierarchies composed of 2 of the same nondecomposable 
        return pairs
    else: 
        return theories


def check_reducible(nd_map: dict): 
    check = {}              #store if found trunk theories for hierarchy already
    reducible = True
    weak_reducible_trunk = {}

    theories = [theory for signature in nd_map for theory in nd_map[signature]['nd']]
    pairs = get_theory_pairs(theories)          
    temp = get_hierarchies_by_type(2)
    candidate_hier = []
    for hier in temp: 
        if hier['nondecomp_hierarchies'] and tuple(hier['nondecomp_hierarchies'].split(',')) in pairs: 
            candidate_hier.append(hier)

    for hier in candidate_hier: 
        name = hier['hierarchy_name']
        if name not in check:
            theories = get_trunk_theories(name)
            if not theories: 
                print('skipping...')
                continue
            check[name] = []
            for t in theories: 
                lines = theory.theory_setup(os.path.join(REPO_PATH, name, t))
                if lines: 
                    check[name].append({
                        'theory_name': t,
                        'lines' : lines
                    })

        # check if all examples falsify all trunk theories, if yes, then it is reducible, if not, then it needs residue axioms 
        for t in check[name]: 
            for ex_file in os.listdir(EX_PATH):
                if ex_file.endswith(".in"):
                    model_lines = model.model_setup(os.path.join(EX_PATH, ex_file), closed_world=True)
                    if relationship.consistency(model_lines, t['lines'],new_dir=""):
                        reducible = False
                        if name not in weak_reducible_trunk: 
                            weak_reducible_trunk[name] = set()
                        weak_reducible_trunk[name].add(t['theory_name'])
    print(reducible, weak_reducible_trunk)
    return reducible, weak_reducible_trunk


if __name__ == "__main__": 
    nd_map = nondecomp()
    if nd_map: 
        reducible, trunk = check_reducible(nd_map)
        if not reducible:       #run hashemi on weakly reducible hierarchies
            for hier in trunk: 
                hashemi(hier)
        else: 
            hierarchies = set()
            results = []
            for signature in nd_map: 
                for hier in nd_map[signature]['nd']: 
                    hierarchies.add(hier)
            for hier in list(hierarchies): 
                results.append(hashemi(hier))
            
