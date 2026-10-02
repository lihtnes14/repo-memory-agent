import sqlite3
from datetime import datetime


DATABASE_PATH = "memory.sqlite"


def get_connection():
    return sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )


def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            content TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            importance REAL DEFAULT 0.5,
            created_at TEXT NOT NULL,
            last_accessed TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_memory(
    user_id: str,
    project_id: str,
    content: str,
    memory_type: str,
    importance: float
):

    conn = get_connection()

    cursor = conn.cursor()

    now = datetime.utcnow().isoformat()

    cursor.execute(
        """
        INSERT INTO memories (
            user_id,
            project_id,
            content,
            memory_type,
            importance,
            created_at,
            last_accessed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            project_id,
            content,
            memory_type,
            importance,
            now,
            now,
        )
    )

    conn.commit()

    memory_id = cursor.lastrowid

    conn.close()

    return memory_id


def get_memories(
    user_id: str,
    project_id: str
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            content,
            memory_type,
            importance,
            created_at,
            last_accessed
        FROM memories
        WHERE user_id = ?
        AND project_id = ?
        ORDER BY importance DESC, last_accessed DESC
        """,
        (
            user_id,
            project_id,
        )
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def update_memory(
    memory_id: int,
    content: str,
    importance: float
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE memories
        SET
            content = ?,
            importance = ?,
            last_accessed = ?
        WHERE id = ?
        """,
        (
            content,
            importance,
            datetime.utcnow().isoformat(),
            memory_id,
        )
    )

    conn.commit()

    conn.close()



