from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from lucifer_os.memory.models import MemoryItem, MemoryScope, MemoryType
from lucifer_os.memory.store import MemoryStore


class SQLiteMemoryStore(MemoryStore):
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = db_path
        self._connection = self._connect(db_path)
        self._connection.row_factory = sqlite3.Row
        self._ensure_schema()

    def add(self, item: MemoryItem) -> MemoryItem:
        self._connection.execute(
            "INSERT OR REPLACE INTO memory_items (id, content, memory_type, scope, source, confidence, tags_json, metadata_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            self._item_to_params(item),
        )
        self._connection.commit()
        return item

    def get(self, memory_id: str) -> MemoryItem | None:
        row = self._connection.execute(
            "SELECT * FROM memory_items WHERE id = ?",
            (memory_id,),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_item(row)

    def list(self, scope: MemoryScope | None = None, type: MemoryType | None = None) -> list[MemoryItem]:
        query = "SELECT * FROM memory_items"
        conditions: list[str] = []
        params: list[Any] = []

        if scope is not None:
            conditions.append("scope = ?")
            params.append(scope.value)

        if type is not None:
            conditions.append("memory_type = ?")
            params.append(type.value)

        if conditions:
            query = query + " WHERE " + " AND ".join(conditions)

        query = query + " ORDER BY created_at ASC, id ASC"

        rows = self._connection.execute(query, params).fetchall()
        return [self._row_to_item(row) for row in rows]

    def update(self, item: MemoryItem) -> bool:
        cursor = self._connection.execute(
            "UPDATE memory_items SET content = ?, memory_type = ?, scope = ?, source = ?, confidence = ?, tags_json = ?, metadata_json = ?, created_at = ?, updated_at = ? WHERE id = ?",
            (
                item.content,
                item.type.value,
                item.scope.value,
                item.source,
                item.confidence,
                json.dumps(list(item.tags), ensure_ascii=False),
                json.dumps(item.metadata, ensure_ascii=False, sort_keys=True),
                item.created_at,
                item.updated_at,
                item.id,
            ),
        )
        self._connection.commit()
        return cursor.rowcount > 0

    def delete(self, memory_id: str) -> bool:
        cursor = self._connection.execute(
            "DELETE FROM memory_items WHERE id = ?",
            (memory_id,),
        )
        self._connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self._connection.close()

    @staticmethod
    def _connect(db_path: str | Path) -> sqlite3.Connection:
        if str(db_path) == ":memory:":
            return sqlite3.connect(":memory:")

        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(path)

    def _ensure_schema(self) -> None:
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS memory_items (id TEXT PRIMARY KEY, content TEXT NOT NULL, memory_type TEXT NOT NULL, scope TEXT NOT NULL, source TEXT NOT NULL, confidence REAL NOT NULL, tags_json TEXT NOT NULL, metadata_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_memory_items_scope ON memory_items(scope)"
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_memory_items_memory_type ON memory_items(memory_type)"
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_memory_items_created_at ON memory_items(created_at)"
        )
        self._connection.commit()

    @staticmethod
    def _item_to_params(item: MemoryItem) -> tuple[Any, ...]:
        return (
            item.id,
            item.content,
            item.type.value,
            item.scope.value,
            item.source,
            item.confidence,
            json.dumps(list(item.tags), ensure_ascii=False),
            json.dumps(item.metadata, ensure_ascii=False, sort_keys=True),
            item.created_at,
            item.updated_at,
        )

    @staticmethod
    def _row_to_item(row: sqlite3.Row) -> MemoryItem:
        tags = tuple(json.loads(row["tags_json"]))
        metadata = json.loads(row["metadata_json"])

        return MemoryItem(
            id=row["id"],
            content=row["content"],
            type=MemoryType(row["memory_type"]),
            scope=MemoryScope(row["scope"]),
            source=row["source"],
            confidence=float(row["confidence"]),
            tags=tags,
            metadata=metadata,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
