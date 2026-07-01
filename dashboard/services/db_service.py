from pathlib import Path
import sqlite3
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "epg_vision.db"


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


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
        job_name TEXT,
        status TEXT,
        message TEXT,
        duration_seconds REAL
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

    frame_path = (
        best.get("archived_frame")
        or best.get("frame_path")
        or best.get("frame")
        or ""
    )

    crop_path = (
        best.get("archived_crop")
        or best.get("crop")
        or ""
    )

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
        frame_path,
        crop_path
    ))

    con.commit()
    con.close()


def record_build_run(job_name, status, message="", duration_seconds=0):
    init_db()

    con = connect()
    cur = con.cursor()

    cur.execute("""
    INSERT INTO build_runs (
        created_at,
        job_name,
        status,
        message,
        duration_seconds
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat() + "Z",
        job_name,
        status,
        message,
        float(duration_seconds or 0)
    ))

    con.commit()
    con.close()


def recent_ocr_results(limit=100):
    init_db()

    con = connect()
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


def channel_ocr_history(provider_file, channel_index, limit=25):
    init_db()

    con = connect()
    cur = con.cursor()

    rows = cur.execute("""
        SELECT *
        FROM ocr_results
        WHERE provider_file = ?
          AND channel_index = ?
        ORDER BY id DESC
        LIMIT ?
    """, (provider_file, channel_index, limit)).fetchall()

    con.close()
    return rows


def recent_build_runs(limit=50):
    init_db()

    con = connect()
    cur = con.cursor()

    rows = cur.execute("""
        SELECT *
        FROM build_runs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()

    con.close()
    return rows


def ocr_stats():
    init_db()

    con = connect()
    cur = con.cursor()

    total = cur.execute("SELECT COUNT(*) FROM ocr_results").fetchone()[0]
    accepted = cur.execute(
        "SELECT COUNT(*) FROM ocr_results WHERE decision = 'ACCEPT'"
    ).fetchone()[0]
    verified = cur.execute(
        "SELECT COUNT(*) FROM ocr_results WHERE decision = 'VERIFY'"
    ).fetchone()[0]
    rejected = cur.execute(
        "SELECT COUNT(*) FROM ocr_results WHERE decision = 'REJECT'"
    ).fetchone()[0]

    avg_conf = cur.execute(
        "SELECT AVG(confidence) FROM ocr_results"
    ).fetchone()[0] or 0

    con.close()

    return {
        "total": total,
        "accepted": accepted,
        "verified": verified,
        "rejected": rejected,
        "average_confidence": round(float(avg_conf), 2),
    }
