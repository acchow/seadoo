INSERT INTO hierarchies VALUES 
    ('graphs', 1, 'undirected_graph'), 
    ('mereograph', 2, ''), 
    ('orderings', 1, 'quasi_order'), 
    ('subgraph', 2, ''), 
    ('subposet', 2, ''), 
    ('successor', 1, '')
;
INSERT INTO weakly_reducible_hierarchies VALUES 
    ('mereograph', 'graphs, orderings'), 
    ('subgraph', 'orderings, orderings'), 
    ('subposet', 'graphs, graphs')
;