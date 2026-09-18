-- The agent's memory. Business data (students, drives, applications) is NOT in here.
-- Run by ConversationStore.migrate(). SQLite: foreign keys are switched on per connection.

-- Given, as the pattern to follow.
CREATE TABLE IF NOT EXISTS thread (
    id          TEXT PRIMARY KEY,
    student_id  TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS message (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id   TEXT NOT NULL,
    seq         INTEGER NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('user', 'model', 'tool')),
    text        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (thread_id) REFERENCES thread(id),
    UNIQUE (thread_id, seq)
);

CREATE TABLE IF NOT EXISTS run (
    id          TEXT PRIMARY KEY,
    thread_id   TEXT NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('running', 'succeeded', 'failed')),
    model       TEXT,
    tokens_in   INTEGER,
    tokens_out  INTEGER,
    error_code  TEXT,
    started_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    finished_at TEXT,
    FOREIGN KEY (thread_id) REFERENCES thread(id)
);

CREATE TABLE IF NOT EXISTS run_step (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      TEXT NOT NULL,
    seq         INTEGER NOT NULL,
    kind        TEXT NOT NULL CHECK (kind IN ('model', 'tool')),
    tokens_in   INTEGER,
    tokens_out  INTEGER,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (run_id) REFERENCES run(id),
    UNIQUE (run_id, seq)
);

CREATE TABLE IF NOT EXISTS tool_call (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_step_id INTEGER NOT NULL,
    tool_name   TEXT NOT NULL,
    args        TEXT NOT NULL,
    result      TEXT NOT NULL,
    ok          INTEGER NOT NULL,
    latency_ms  INTEGER NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (run_step_id) REFERENCES run_step(id),
    UNIQUE (run_step_id)
);