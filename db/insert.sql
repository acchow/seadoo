INSERT INTO hierarchies VALUES 
    ('graphs', '', 1, 'adj', 'undirected_graph'), 
    ('mereograph', 'graphs,orderings', 2, '', ''), 
    ('orderings', '', 1, 'leq', 'quasi_order'), 
    ('subgraph', 'graphs,graphs', 2, '',''),
    ('subposet', 'orderings,orderings', 2, '','')
;