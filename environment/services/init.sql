CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seed INTEGER NOT NULL,
    operand_a INTEGER NOT NULL,
    operand_b INTEGER NOT NULL,
    operator VARCHAR(1) DEFAULT '+',
    correct_answer INTEGER NOT NULL,
    submitted_answer INTEGER,
    reward FLOAT DEFAULT 1.0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    solved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

CREATE TABLE IF NOT EXISTS individuals (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    body_url VARCHAR(256) NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    energy FLOAT DEFAULT 100.0,
    age INTEGER DEFAULT 0,
    tasks_solved INTEGER DEFAULT 0,
    alive BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_individuals_alive ON individuals(alive);
CREATE INDEX IF NOT EXISTS idx_individuals_energy ON individuals(energy);
