import sqlite3
import json
import os
from typing import Dict, Optional
from core.impl.tree import MTTree
from model.store.repo.interfaces.base_tree_repo import IMTStore

class SQLiteTreeRepository(IMTStore):
    """SQLite 기반 트리 저장소 구현체"""
    def __init__(self, db_path: str = "tree.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_table()

    def _init_table(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tree_data (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def save(self, tree: MTTree, tree_id: str | None = None) -> str:
        if tree_id is None:
            tree_id = tree.id
        data = json.dumps(tree.to_dict(), ensure_ascii=False)
        cur = self.conn.cursor()
        cur.execute("REPLACE INTO tree_data (id, data) VALUES (?, ?)", (tree_id, data))
        self.conn.commit()
        return tree_id

    def load(self, tree_id: str) -> MTTree | None:
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM tree_data WHERE id = ?", (tree_id,))
        row = cur.fetchone()
        if row:
            tree_data = json.loads(row[0])
            return MTTree.from_dict(tree_data)
        return None

    def delete(self, tree_id: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM tree_data WHERE id = ?", (tree_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def list_trees(self) -> Dict[str, str]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, data FROM tree_data")
        result = {}
        for row in cur.fetchall():
            tree_id, data = row
            try:
                tree_data = json.loads(data)
                tree_name = tree_data.get("name", tree_id)
            except Exception:
                tree_name = tree_id
            result[tree_id] = tree_name
        return result 