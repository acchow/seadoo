INSERT INTO hierarchies VALUES 
    ('graphs', '', 1, 'undirected_graph'), 
    ('mereograph', 'graphs,orderings', 2, ''), 
    ('orderings', '', 1, 'quasi_order'), 
    ('subgraph', 'graphs,graphs', 2, ''),
    ('subposet', 'orderings,orderings', 2, '')
;