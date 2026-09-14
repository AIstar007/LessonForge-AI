import sqlite3
from pathlib import Path
from datetime import datetime


class MemoryStore:
    def __init__(self, db_path="data/memory.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS failures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            topic TEXT,
            attempt INTEGER,
            failed_checks TEXT,
            reasons TEXT,
            fixes TEXT,
            created_at TEXT
        )
        ''')
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            topic TEXT,
            status TEXT,
            attempts_used INTEGER,
            created_at TEXT
        )
        ''')
        self.conn.commit()

    def save_failure(self, run_id, topic, attempt, failed_checks, reasons, fixes):
        self.conn.execute(
            '''INSERT INTO failures
            (run_id, topic, attempt, failed_checks, reasons, fixes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                run_id, topic, attempt,
                " | ".join(failed_checks),
                " | ".join(reasons),
                " | ".join(fixes),
                datetime.utcnow().isoformat()
            )
        )
        self.conn.commit()

    def save_run(self, run_id, topic, status, attempts_used):
        self.conn.execute(
            '''INSERT OR REPLACE INTO runs
            (run_id, topic, status, attempts_used, created_at)
            VALUES (?, ?, ?, ?, ?)''',
            (run_id, topic, status, attempts_used, datetime.utcnow().isoformat())
        )
        self.conn.commit()

    def learned_patterns(self, limit=10):
        rows = self.conn.execute(
            '''SELECT failed_checks, fixes FROM failures
               ORDER BY id DESC LIMIT ?''', (limit,)
        ).fetchall()
        return [
            f"Past failure [{checks}] -> recommended fix: {fixes}"
            for checks, fixes in rows
        ]

    def recent_runs(self, limit=20):
        return self.conn.execute(
            '''SELECT run_id, topic, status, attempts_used, created_at
               FROM runs ORDER BY created_at DESC LIMIT ?''', (limit,)
        ).fetchall()
