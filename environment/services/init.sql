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
