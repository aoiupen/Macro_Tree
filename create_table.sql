CREATE TABLE tree_nodes (
    id SERIAL PRIMARY KEY,
    parent_id INT REFERENCES tree_nodes(id) ON DELETE CASCADE, 
    name TEXT NOT NULL, 
    inp TEXT,           
    sub_con TEXT,       
    sub TEXT            
);