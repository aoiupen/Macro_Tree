CREATE TABLE tree_nodes (
    id SERIAL PRIMARY KEY,
    parent_id INT REFERENCES tree_nodes(id) ON DELETE CASCADE, 
    name TEXT NOT NULL, 
    inp TEXT,           
    sub_con TEXT,       
    sub TEXT            
);

CREATE TABLE tree_states (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    state JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tree_snapshots (
    id SERIAL PRIMARY KEY,
    tree_state_id INT REFERENCES tree_states(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    snapshot JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 이전 테이블 삭제 (필요 시 주석 해제)
-- DROP TABLE IF EXISTS tree_nodes CASCADE;