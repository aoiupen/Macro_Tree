import sqlite3
import json
from model.store.repo.base_store import ITreeStore

class SQLiteTreeStore(ITreeStore):
    def __init__(self, db_path="tree.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_table()

    def _init_table(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tree_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def save(self, tree):
        data = json.dumps(tree.to_dict(), ensure_ascii=False)
        cur = self.conn.cursor()
        cur.execute("DELETE FROM tree_data")  # 항상 1개만 저장
        cur.execute("INSERT INTO tree_data (data) VALUES (?)", (data,))
        self.conn.commit()

    def load(self):
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM tree_data ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return None 