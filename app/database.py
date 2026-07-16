from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator, Optional

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

from .config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    locale      TEXT NOT NULL DEFAULT 'es',
    theme       TEXT NOT NULL DEFAULT 'light',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS records (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind            TEXT NOT NULL CHECK (kind IN ('income','expense')),
    name            TEXT NOT NULL,
    occurred_at     TEXT NOT NULL,
    amount          NUMERIC(12,2) NOT NULL,
    payment_method  TEXT NOT NULL CHECK (payment_method IN ('cash','card','zelle')),
    note            TEXT DEFAULT '',
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_records_user_kind_time
    ON records(user_id, kind, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_records_user_time
    ON records(user_id, occurred_at DESC);
"""


_pool: Optional[ThreadedConnectionPool] = None


def _get_pool() -> ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
    return _pool


@contextmanager
def get_conn() -> Iterator[psycopg2.extensions.connection]:
    pool = _get_pool()
    conn = pool.getconn()
    try:
        conn.set_session(autocommit=True)
        yield conn
    finally:
        pool.putconn(conn)


def init_db() -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _row_to_dict(row: tuple, cur: psycopg2.extras.RealDictCursor) -> dict:
    cols = [desc[0] for desc in cur.description]
    return dict(zip(cols, row))


# ── Users ──────────────────────────────────────────────────────────────────────


def create_user(name: str, locale: str = "es") -> dict:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO users(name, locale, created_at) "
                "VALUES (%s, %s, %s) "
                "ON CONFLICT (name) DO UPDATE SET locale = EXCLUDED.locale "
                "RETURNING id, name, locale, theme, created_at",
                (name.strip(), locale, now_iso()),
            )
            return dict(cur.fetchone())


def get_user_by_id(user_id: int) -> Optional[dict]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, name, locale, theme, created_at FROM users WHERE id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None


def update_user_prefs(user_id: int, *, locale: str | None = None, theme: str | None = None) -> None:
    parts, params = [], []
    if locale is not None:
        parts.append("locale = %s")
        params.append(locale)
    if theme is not None:
        parts.append("theme = %s")
        params.append(theme)
    if not parts:
        return
    params.append(user_id)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE users SET {', '.join(parts)} WHERE id = %s", params)


# ── Records ────────────────────────────────────────────────────────────────────


def insert_record(
    user_id: int,
    *,
    kind: str,
    name: str,
    occurred_at: str,
    amount: float,
    payment_method: str,
    note: str = "",
) -> dict:
    ts = now_iso()
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO records(user_id, kind, name, occurred_at, amount, payment_method, note, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "RETURNING *",
                (user_id, kind, name.strip(), occurred_at, amount, payment_method, note, ts, ts),
            )
            return dict(cur.fetchone())


def get_record_by_id(record_id: int, user_id: int) -> Optional[dict]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM records WHERE id = %s AND user_id = %s",
                (record_id, user_id),
            )
            row = cur.fetchone()
            return dict(row) if row else None


def update_record(
    record_id: int,
    user_id: int,
    *,
    kind: str | None = None,
    name: str | None = None,
    occurred_at: str | None = None,
    amount: float | None = None,
    payment_method: str | None = None,
    note: str | None = None,
) -> Optional[dict]:
    parts, params = [], []
    if kind is not None:
        parts.append("kind = %s")
        params.append(kind)
    if name is not None:
        parts.append("name = %s")
        params.append(name.strip())
    if occurred_at is not None:
        parts.append("occurred_at = %s")
        params.append(occurred_at)
    if amount is not None:
        parts.append("amount = %s")
        params.append(amount)
    if payment_method is not None:
        parts.append("payment_method = %s")
        params.append(payment_method)
    if note is not None:
        parts.append("note = %s")
        params.append(note)
    if not parts:
        return get_record_by_id(record_id, user_id)
    parts.append("updated_at = %s")
    params.extend([now_iso(), record_id, user_id])
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                f"UPDATE records SET {', '.join(parts)} "
                "WHERE id = %s AND user_id = %s RETURNING *",
                params,
            )
            row = cur.fetchone()
            return dict(row) if row else None


def delete_record(record_id: int, user_id: int) -> bool:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM records WHERE id = %s AND user_id = %s",
                (record_id, user_id),
            )
            return cur.rowcount > 0


def list_records(
    user_id: int,
    *,
    kind: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> list[dict]:
    clauses = ["user_id = %s"]
    params: list = [user_id]
    if kind:
        clauses.append("kind = %s")
        params.append(kind)
    if from_date:
        clauses.append("occurred_at >= %s")
        params.append(from_date)
    if to_date:
        clauses.append("occurred_at <= %s")
        params.append(to_date)
    where = " AND ".join(clauses)
    params.extend([max(1, limit), max(0, offset)])
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                f"SELECT * FROM records WHERE {where} "
                "ORDER BY occurred_at DESC, id DESC "
                "LIMIT %s OFFSET %s",
                params,
            )
            return [dict(r) for r in cur.fetchall()]


def get_month_summary(user_id: int, year: int, month: int) -> dict:
    prefix = f"{year:04d}-{month:02d}"
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT kind, COALESCE(SUM(amount), 0) AS total "
                "FROM records WHERE user_id = %s AND occurred_at LIKE %s "
                "GROUP BY kind",
                (user_id, f"{prefix}%"),
            )
            rows = cur.fetchall()
            result = {"income": 0, "expense": 0}
            for r in rows:
                result[r["kind"]] = float(r["total"])
            result["balance"] = result["income"] - result["expense"]
            return result


def get_recent_records(user_id: int, limit: int = 5) -> list[dict]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM records WHERE user_id = %s "
                "ORDER BY occurred_at DESC, id DESC LIMIT %s",
                (user_id, max(1, limit)),
            )
            return [dict(r) for r in cur.fetchall()]


def is_healthy() -> bool:
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False
