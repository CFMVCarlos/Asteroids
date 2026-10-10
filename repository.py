"""Database repository module for Asteroids."""

import sqlite3
from typing import TypedDict


class HighScore(TypedDict):
    """Structured representation of a high score record."""

    id: int
    player_name: str
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
        """Create the high_scores table and perform schema migrations."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS high_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL DEFAULT 'PILOT',
                score INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Check if legacy table without player_name column exists
        cursor.execute("PRAGMA table_info(high_scores)")
        columns = [col[1] for col in cursor.fetchall()]
        if "player_name" not in columns:
            cursor.execute(
                "ALTER TABLE high_scores ADD COLUMN player_name TEXT NOT NULL DEFAULT 'PILOT'"
            )
        self.conn.commit()

    def save_score(self, score: int, player_name: str = "PILOT") -> None:
        """Save a new high score with player name to the database."""
        cursor = self.conn.cursor()
        sanitized_name = player_name.strip()[:10] if player_name.strip() else "PILOT"
        cursor.execute(
            "INSERT INTO high_scores (player_name, score) VALUES (?, ?)",
            (sanitized_name, score),
        )
        self.conn.commit()

    def get_top_scores(self, limit: int = 5) -> list[HighScore]:
        """Retrieve the top high scores."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, player_name, score, created_at FROM high_scores ORDER BY score DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [
            {"id": row[0], "player_name": row[1], "score": row[2], "created_at": row[3]}
            for row in rows
        ]
