"""
database.py — SPARK SQLite Database Module
==========================================
Handles all persistent storage for inspection records and image file paths.
Records are stored locally in data/spark.db.

Schema
------
repair_records : one row per inspection record
image_store    : maps record_id -> file paths for reference/current/highlighted images
"""

from __future__ import annotations

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "spark.db"
IMG_STORE_DIR = DATA_DIR / "inspection_images"

DATA_DIR.mkdir(exist_ok=True)
IMG_STORE_DIR.mkdir(exist_ok=True)


# ── Connection helper ────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


# ── Schema initialisation ────────────────────────────────────────────────────

def init_db() -> None:
    """Create tables if they do not already exist."""
    with _get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS repair_records (
                record_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                gearbox_case    TEXT    NOT NULL,
                technician_name TEXT    NOT NULL,
                inspection_date TEXT    NOT NULL,
                change_percent  REAL    DEFAULT 0.0,
                comparison_summary TEXT DEFAULT '',
                observations    TEXT    DEFAULT '',
                repair_actions  TEXT    DEFAULT '',
                status          TEXT    NOT NULL DEFAULT 'Pending Review',
                created_at      TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS image_store (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id       INTEGER NOT NULL UNIQUE,
                reference_path  TEXT    DEFAULT '',
                current_path    TEXT    DEFAULT '',
                highlighted_path TEXT   DEFAULT '',
                FOREIGN KEY (record_id) REFERENCES repair_records(record_id)
            );
            """
        )


# ── Record CRUD ──────────────────────────────────────────────────────────────

def save_record(
    *,
    gearbox_case: str,
    technician_name: str,
    inspection_date: str,
    change_percent: float = 0.0,
    comparison_summary: str = "",
    observations: str = "",
    repair_actions: str = "",
    status: str = "Pending Review",
) -> int:
    """Insert a new repair record. Returns the new record_id."""
    created_at = datetime.now().isoformat(sep=" ", timespec="seconds")
    with _get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO repair_records
                (gearbox_case, technician_name, inspection_date,
                 change_percent, comparison_summary,
                 observations, repair_actions, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                gearbox_case,
                technician_name,
                inspection_date,
                change_percent,
                comparison_summary,
                observations,
                repair_actions,
                status,
                created_at,
            ),
        )
        return cur.lastrowid


def update_status(record_id: int, status: str) -> None:
    """Update the review status of an existing record."""
    with _get_conn() as conn:
        conn.execute(
            "UPDATE repair_records SET status = ? WHERE record_id = ?",
            (status, record_id),
        )


def get_all_records(status_filter: Optional[str] = None) -> list[dict]:
    """
    Return all repair records, optionally filtered by status.
    Each record is returned as a plain dict.
    """
    with _get_conn() as conn:
        if status_filter and status_filter != "All":
            rows = conn.execute(
                "SELECT * FROM repair_records WHERE status = ? ORDER BY record_id DESC",
                (status_filter,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM repair_records ORDER BY record_id DESC"
            ).fetchall()
    return [dict(row) for row in rows]


def get_record_by_id(record_id: int) -> Optional[dict]:
    """Return a single record dict or None if not found."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM repair_records WHERE record_id = ?",
            (record_id,),
        ).fetchone()
    return dict(row) if row else None


def count_by_status() -> dict[str, int]:
    """Return counts for each status and a total."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS cnt FROM repair_records GROUP BY status"
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) AS cnt FROM repair_records"
        ).fetchone()["cnt"]
    counts = {row["status"]: row["cnt"] for row in rows}
    counts["Total"] = total
    return counts


def get_recent_records(limit: int = 5) -> list[dict]:
    """Return the most recently created records."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM repair_records ORDER BY record_id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


# ── Image persistence ────────────────────────────────────────────────────────

def save_images_for_record(
    record_id: int,
    reference_path: Optional[str] = None,
    current_path: Optional[str] = None,
    highlighted_path: Optional[str] = None,
) -> None:
    """
    Copy image files into the persistent store and record their new paths.
    Skips any path that is None or points to a non-existent file.
    """
    def _copy(src: Optional[str], suffix: str) -> str:
        if not src:
            return ""
        src_p = Path(src)
        if not src_p.exists():
            return ""
        dest = IMG_STORE_DIR / f"rec{record_id}_{suffix}{src_p.suffix}"
        shutil.copy2(src_p, dest)
        return str(dest)

    ref_dest = _copy(reference_path, "reference")
    cur_dest = _copy(current_path, "current")
    hl_dest = _copy(highlighted_path, "highlighted")

    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO image_store (record_id, reference_path, current_path, highlighted_path)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(record_id) DO UPDATE SET
                reference_path  = excluded.reference_path,
                current_path    = excluded.current_path,
                highlighted_path = excluded.highlighted_path
            """,
            (record_id, ref_dest, cur_dest, hl_dest),
        )


def get_images_for_record(record_id: int) -> dict[str, str]:
    """Return image paths for a record (empty strings if not stored)."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM image_store WHERE record_id = ?",
            (record_id,),
        ).fetchone()
    if row:
        return {
            "reference_path": row["reference_path"] or "",
            "current_path": row["current_path"] or "",
            "highlighted_path": row["highlighted_path"] or "",
        }
    return {"reference_path": "", "current_path": "", "highlighted_path": ""}


# ── Module init ──────────────────────────────────────────────────────────────
init_db()
