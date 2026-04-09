"""Temporary SQLite persistence for contributor task demo state.

Default file: temp_api_db/contributor_tasks.sqlite (delete the whole temp_api_db folder to reset).
Override with CONTRIBUTOR_TASKS_DB.
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "temp_api_db" / "contributor_tasks.sqlite"


def get_db_path() -> Path:
    env = os.environ.get("CONTRIBUTOR_TASKS_DB")
    return Path(env) if env else DEFAULT_DB_PATH


def _json_default(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def dumps(obj: Any) -> str:
    return json.dumps(obj, default=_json_default, ensure_ascii=False)


def loads(s: str) -> Any:
    return json.loads(s)


@dataclass
class FullState:
    tasks: dict[str, dict[str, Any]]
    workroom: dict[str, dict[str, Any]]
    timelines: dict[str, list[dict[str, Any]]]
    declined: list[str]
    profile: dict[str, Any]


def init_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS app_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            tasks_json TEXT NOT NULL,
            workroom_json TEXT NOT NULL,
            timelines_json TEXT NOT NULL,
            declined_json TEXT NOT NULL,
            profile_json TEXT NOT NULL
        )
        """
    )
    conn.commit()


def load_state(path: Path | None = None) -> FullState | None:
    p = path or get_db_path()
    if not p.exists():
        return None
    conn = sqlite3.connect(str(p))
    try:
        init_schema(conn)
        row = conn.execute("SELECT tasks_json, workroom_json, timelines_json, declined_json, profile_json FROM app_state WHERE id = 1").fetchone()
        if not row:
            return None
        tasks, workroom, timelines, declined, profile = (loads(x) for x in row)
        return FullState(
            tasks=tasks,
            workroom=workroom,
            timelines=timelines,
            declined=declined,
            profile=profile,
        )
    finally:
        conn.close()


def save_state(
    state: FullState,
    path: Path | None = None,
) -> None:
    p = path or get_db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    try:
        init_schema(conn)
        conn.execute(
            """
            INSERT INTO app_state (id, tasks_json, workroom_json, timelines_json, declined_json, profile_json)
            VALUES (1, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              tasks_json = excluded.tasks_json,
              workroom_json = excluded.workroom_json,
              timelines_json = excluded.timelines_json,
              declined_json = excluded.declined_json,
              profile_json = excluded.profile_json
            """,
            (
                dumps(state.tasks),
                dumps(state.workroom),
                dumps(state.timelines),
                dumps(state.declined),
                dumps(state.profile),
            ),
        )
        conn.commit()
    finally:
        conn.close()
