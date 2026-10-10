"""Database repository module for Asteroids."""

import sqlite3
from typing import TypedDict


class HighScore(TypedDict):
    """Structured representation of a high score record."""

    id: int
    score: int
    created_at: str


class HighScoreRepository:
    """Repository for managing high score persistence using SQLite."""

    def __init__(self, db_path: str = "asteroids.db") -> None:
        """Initialize the repository and create the table if it doesn't exist."""
        self.db_path = db_path
        # Use an in-memory database if :memory: is provided, and keep connection open
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        """Create the high_scores table."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS high_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def save_score(self, score: int) -> None:
        """Save a new high score to the database."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO high_scores (score) VALUES (?)", (score,))
        self.conn.commit()

    def get_top_scores(self, limit: int = 5) -> list[HighScore]:
        """Retrieve the top high scores."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, score, created_at FROM high_scores ORDER BY score DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [{"id": row[0], "score": row[1], "created_at": row[2]} for row in rows]
