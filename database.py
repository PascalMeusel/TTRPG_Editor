import sqlite3
import json
import os

class Database:
    def __init__(self, campaign_path):
        self.db_path = os.path.join(campaign_path, 'campaign.db')
        self.conn = None

    def connect(self):
        """Establishes a connection to the database and ensures schema exists."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize_schema()

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

    def execute(self, query, params=()):
        """Executes a query that doesn't return data (INSERT, UPDATE, DELETE)."""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()

    def fetchone(self, query, params=()):
        """Fetches a single record."""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query, params=()):
        """Fetches all records."""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def _initialize_schema(self):
        """Creates all necessary tables if they don't exist."""
        # Using TEXT to store JSON blobs for flexibility.
        # Indexing key fields for fast lookups.
        schema = [
            """
            CREATE TABLE IF NOT EXISTS characters (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                rule_set TEXT NOT NULL,
                data TEXT NOT NULL
            );
            """,
            "CREATE INDEX IF NOT EXISTS idx_char_name ON characters (name);",
            "CREATE INDEX IF NOT EXISTS idx_char_ruleset ON characters (rule_set);",
            """
            CREATE TABLE IF NOT EXISTS npcs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                rule_set TEXT NOT NULL,
                data TEXT NOT NULL
            );
            """,
            "CREATE INDEX IF NOT EXISTS idx_npc_name ON npcs (name);",
            "CREATE INDEX IF NOT EXISTS idx_npc_ruleset ON npcs (rule_set);",
            """
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS quests (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            );
            """
        ]
        
        cursor = self.conn.cursor()
        for statement in schema:
            cursor.execute(statement)
        self.conn.commit()