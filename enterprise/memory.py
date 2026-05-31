import sqlite3
from datetime import datetime, timezone

from .config import STORE_DIR


DB_PATH = STORE_DIR / "assistant.db"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            create table if not exists messages (
                id integer primary key autoincrement,
                conversation_id text not null,
                role text not null,
                content text not null,
                created_at text not null
            )
            """
        )
        connection.execute(
            """
            create table if not exists analytics (
                id integer primary key autoincrement,
                event text not null,
                payload text not null,
                created_at text not null
            )
            """
        )


def add_message(conversation_id: str, role: str, content: str) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "insert into messages (conversation_id, role, content, created_at) values (?, ?, ?, ?)",
            (conversation_id, role, content, datetime.now(timezone.utc).isoformat()),
        )


def get_history(conversation_id: str, limit: int = 8) -> list[dict]:
    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            """
            select role, content from messages
            where conversation_id = ?
            order by id desc
            limit ?
            """,
            (conversation_id, limit),
        ).fetchall()
    return [{"role": role, "content": content} for role, content in reversed(rows)]


def record_event(event: str, payload: str) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "insert into analytics (event, payload, created_at) values (?, ?, ?)",
            (event, payload, datetime.now(timezone.utc).isoformat()),
        )


def analytics_summary() -> dict:
    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            "select event, count(*) from analytics group by event order by event"
        ).fetchall()
    return {event: count for event, count in rows}
