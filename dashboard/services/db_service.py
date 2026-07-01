from pathlib import Path
import sqlite3
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "epg_vision.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ocr_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        provider_file TEXT,
        provider_label TEXT,
        channel_index INTEGER,
        channel_id TEXT,
        channel_name TEXT,
        raw_text TEXT,
        clean_title TEXT,
        matched_title TEXT,
        confidence REAL,
        match_score REAL,
        vote_count INTEGER,
        vote_avg_confidence REAL,
        decision TEXT,
        decision_score REAL,
        frame_path TEXT,
        crop_path TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS build_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        status TEXT,
        message TEXT
    )
    """)

    con.commit()
    con.close()

def record_ocr_result(
    provider_file,
    provider_label,
    channel_index,
    channel,
    best,
    matched_title,
    match_score,
    decision,
    decision_score
):
    init_db()

    con = connect()
    cur = con.cursor()

    cur.execute("""
    INSERT INTO ocr_results (
        created_at,
        provider_file,
        provider_label,
        channel_index,
        channel_id,
        channel_name,
        raw_text,
        clean_title,
        matched_title,
        confidence,
        match_score,
        vote_count,
        vote_avg_confidence,
        decision,
        decision_score,
        frame_path,
        crop_path
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat() + "Z",
        provider_file,
        provider_label,
        channel_index,
        channel.get("id", ""),
        channel.get("name", ""),
        best.get("raw", ""),
        best.get("clean", ""),
        matched_title,
        float(best.get("confidence", 0)),
        float(match_score or 0),
        int(best.get("vote_count", 1)),
        float(best.get("vote_avg_confidence", best.get("confidence", 0))),
        decision,
        float(decision_score or 0),
        best.get("frame", ""),
        best.get("crop", "")
    ))

    con.commit()
    con.close()

def recent_ocr_results(limit=50):
    init_db()
    con = connect()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    rows = cur.execute("""
        SELECT *
        FROM ocr_results
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()

    con.close()
    return rows

def latest_channel_result(provider_file, channel_index):
    init_db()
    con = connect()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    row = cur.execute("""
        SELECT *
        FROM ocr_results
        WHERE provider_file = ?
          AND channel_index = ?
        ORDER BY id DESC
        LIMIT 1
    """, (provider_file, channel_index)).fetchone()

    con.close()
    return row
