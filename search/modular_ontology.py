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


def nondecomp() -> dict: 
    #generalize
    nd = get_hierarchies_by_type(1)   # 1 relation for nondecomp 
    nd_map = {}                       # key is model signature, value is dict with info 

    # get signatures and respective axioms from examples 
    for ex_file in os.listdir(EX_PATH):
        if ex_file.endswith(".in"):
            model_lines, constants = model.model_setup(os.path.join(EX_PATH, ex_file), closed_world=False)
            temp = model.extract_signatures(model_lines)
            nd_map.update(temp)

    # close model afterward for separate signatures
    for key in nd_map: 
        constants = model.extract_constants(nd_map[key]['asser'])
        closed_lines = model.closed_model(nd_map[key]['asser'], constants, key, nd_map[key]['args'])
        nd_map[key]['asser'] += closed_lines

    # compare the axioms for each signature with every root theory 
    for key in nd_map: 
        print('\nfinding nondecomposable hierarchy match for', key, 'relation signature')
        nd_map[key]['nd'] = None
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
            
            # add a mapping axiom 
            rel = hier['relation_name']
            if rel: 
                map_axiom = '(all x all y ((' + key + '(x,y) <-> ' + rel + '(x,y))))'
                nd_map[key]['asser'].append(map_axiom)

            # consistency check with examples 
            rt_lines = theory.theory_setup(rt_path)
            consistent = relationship.consistency(nd_map[key]['asser'], rt_lines, new_dir="")
            if consistent is True: 
                nd_map[key]['nd'] = hier['hierarchy_name']
            else: 
                # remove mapping axiom for this hierarchy 
                nd_map[key]['asser'].remove(map_axiom)

        if nd_map[key]['nd'] is None: 
            print('inconsistent with all nd hierarchies')
        else: 
            print(key,'\n-> consistent with', nd_map[key]['nd'])
    return nd_map


def get_trunk_theories(hier: str) -> list: 
    trunk_theory_list = []
    path = os.path.join(os.path.sep, REPO_PATH, hier, hier + ".csv")
    try:
        trunk_df = pd.read_csv(path, usecols=[1]).values.tolist()
    except FileNotFoundError: 
        print('\n', path, 'chain decomposition not found. unable to search.')
        return False
    except pd.errors.EmptyDataError: 
        print('\n', path, 'chain decomposition is empty. unable to search.')
        return False
    trunk_df = [t for t in trunk_df if list(filter(lambda a: pd.notna(a), t))]
    trunk_theory_list = list(set(str(s)[2:-2] + ".in" for s in trunk_df))
    return trunk_theory_list


def get_theory_pairs(theories: list) -> list:
    check = {}
    print(list(itertools.permutations(list(set(theories)),2)))
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
    model_lines = []
    check = {}              #store if found trunk theories for hierarchy already
    reducible = True
    weak_reducible_trunk = {}

    # get nd matches and set up model for trunk theory comparisons
    nd_hier = []
    for key in nd_map: 
        nd_match = nd_map[key]['nd']
        if nd_match is not None: 
            nd_hier.append(nd_match)
            model_lines.extend(nd_map[key]['asser'])
    
    # get combinations and retrieve weak reducible hierarchies
    pairs = list(itertools.combinations(sorted(list(set(nd_hier))),2))
    temp = get_hierarchies_by_type(2)
    candidate_hier = []
    for hier in temp: 
        if hier['nondecomp_hierarchies'] and tuple(hier['nondecomp_hierarchies'].split(',')) in pairs: 
            candidate_hier.append(hier)

    # get trunk theories 
    for hier in candidate_hier: 
        name = hier['hierarchy_name']
        if name not in check:
            theories = get_trunk_theories(name)
            if not theories: 
                print('no trunk theories. skipping...')
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
            if relationship.consistency(model_lines, t['lines'],new_dir="") is True:
                reducible = False
                if name not in weak_reducible_trunk: 
                    weak_reducible_trunk[name] = set()
                weak_reducible_trunk[name].add(t['theory_name'])

    return reducible, weak_reducible_trunk


if __name__ == "__main__": 
    nd_map = nondecomp()
    results = []
    if nd_map: 
        reducible, trunk = check_reducible(nd_map)
        if not reducible:               #run hashemi on weakly reducible hierarchies
            print('\nweakly reducible. searching for residue axioms...')
            for hier in trunk: 
                results.extend(hashemi(hier,report=False))
            generate_answer_report('weak_reducible_module', ', '.join(trunk.keys()), results)
        else: 
            print('\nreducible. combining axioms...')
            hierarchies = set()

            for signature in nd_map: 
                hierarchies.add(nd_map[signature]['nd'])

            hierarchies = list(hierarchies)
            for hier in hierarchies: 
                results.extend(hashemi(hier,report=False))
            generate_answer_report('reducible_module', '-'.join(hierarchies), results)
    else: 
        generate_answer_report('no_match','', ['inconsistent with all nondecomposable hierarchies'])
            
