from search.hashemi import *


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
    cols = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{}' AND TABLE_NAME = '{}'".format(config.db['schema'], 'hierarchies')
    cursor.execute(cols)
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
            for s in temp: 
                if s not in nd_map: 
                    nd_map.update(temp)
                    nd_map[s]['axioms'] = [temp[s]['axioms']]
                else: 
                    nd_map[s]['axioms'].append(temp[s]['axioms'])

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
            for ex in nd_map[key]['axioms']: 
                if not relationship.consistency(ex, rt_lines, new_dir=""): 
                    consistent = False
            if consistent: 
                nd_map[key]['nd'].append(hier['hierarchy_name'])
        
        if not nd_map[key]['nd']: 
            print('inconsistent with all nd hierarchies')
        else: 
            print(key,'is consistent with', nd_map[key]['nd'])

    print(nd_map)
    return nd_map


if __name__ == "__main__": 
    nondecomp()


