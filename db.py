from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "database.sqlite3")).resolve()


@dataclass
class ReportEntry:
    semana: str
    dia: str
    total_horas: int
    observaciones: str


@dataclass
class Report:
    id: int
    created_at: str
    entries: List[ReportEntry]

    @property
    def total_horas(self) -> int:
        return sum(entry.total_horas for entry in self.entries)


def _connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS report_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                semana TEXT NOT NULL,
                dia TEXT NOT NULL,
                total_horas INTEGER NOT NULL,
                observaciones TEXT NOT NULL,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            )
            """
        )
        conn.commit()


def create_report(entries: List[ReportEntry]) -> int:
    with _connection() as conn:
        cur = conn.execute(
            "INSERT INTO reports (created_at) VALUES (?)",
            (datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),),
        )
        report_id = cur.lastrowid

        for entry in entries:
            conn.execute(
                """
                INSERT INTO report_entries (report_id, semana, dia, total_horas, observaciones)
                VALUES (?, ?, ?, ?, ?)
                """,
                (report_id, entry.semana, entry.dia, entry.total_horas, entry.observaciones),
            )

        conn.commit()

    return int(report_id)


def add_entries_to_report(report_id: int, entries: List[ReportEntry]) -> bool:
    with _connection() as conn:
        report_exists = conn.execute("SELECT 1 FROM reports WHERE id = ?", (report_id,)).fetchone()
        if not report_exists:
            return False

        for entry in entries:
            conn.execute(
                """
                INSERT INTO report_entries (report_id, semana, dia, total_horas, observaciones)
                VALUES (?, ?, ?, ?, ?)
                """,
                (report_id, entry.semana, entry.dia, entry.total_horas, entry.observaciones),
            )

        conn.commit()

    return True


def delete_report(report_id: int) -> bool:
    with _connection() as conn:
        report_exists = conn.execute("SELECT 1 FROM reports WHERE id = ?", (report_id,)).fetchone()
        if not report_exists:
            return False

        conn.execute("DELETE FROM report_entries WHERE report_id = ?", (report_id,))
        conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()

    return True


def get_report(report_id: int) -> Optional[Report]:
    with _connection() as conn:
        report_row = conn.execute("SELECT id, created_at FROM reports WHERE id = ?", (report_id,)).fetchone()
        if not report_row:
            return None

        entry_rows = conn.execute(
            "SELECT semana, dia, total_horas, observaciones FROM report_entries WHERE report_id = ? ORDER BY id",
            (report_id,),
        ).fetchall()

    entries = [
        ReportEntry(
            semana=row["semana"],
            dia=row["dia"],
            total_horas=row["total_horas"],
            observaciones=row["observaciones"],
        )
        for row in entry_rows
    ]

    return Report(id=report_row["id"], created_at=report_row["created_at"], entries=entries)


def list_reports(limit: int = 10) -> List[Report]:
    with _connection() as conn:
        report_rows = conn.execute(
            "SELECT id, created_at FROM reports ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [Report(id=row["id"], created_at=row["created_at"], entries=[]) for row in report_rows]
