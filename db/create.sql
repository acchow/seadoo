CREATE TABLE hierarchies (
	hierarchy_name varchar(255),
	num_prim_relations int NOT NULL,
	root_theory varchar(255),
	PRIMARY KEY (hierarchy_name)
);
CREATE TABLE weakly_reducible_hierarchies (
	hierarchy_name varchar(255),
	nondecomp_hierarchies varchar(255),
	PRIMARY KEY (hierarchy_name)
);