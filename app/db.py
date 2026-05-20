from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


ADDITIONAL_COLUMNS = {
    "douyin_id": "TEXT NOT NULL DEFAULT ''",
    "web_profile_url": "TEXT NOT NULL DEFAULT ''",
    "creator_level": "INTEGER NOT NULL DEFAULT 0",
    "video_count": "INTEGER NOT NULL DEFAULT 0",
    "like_fan_ratio": "REAL NOT NULL DEFAULT 0",
    "settlement_range": "TEXT NOT NULL DEFAULT ''",
    "settlement_min": "REAL NOT NULL DEFAULT 0",
    "settlement_max": "REAL NOT NULL DEFAULT 0",
    "settlement_mid": "REAL NOT NULL DEFAULT 0",
}


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS influencers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nickname TEXT NOT NULL,
                    profile_url TEXT NOT NULL UNIQUE,
                    douyin_id TEXT NOT NULL DEFAULT '',
                    web_profile_url TEXT NOT NULL DEFAULT '',
                    fans INTEGER NOT NULL DEFAULT 0,
                    category TEXT NOT NULL DEFAULT '',
                    sales_30d INTEGER NOT NULL DEFAULT 0,
                    gmv_30d REAL NOT NULL DEFAULT 0,
                    product_count INTEGER NOT NULL DEFAULT 0,
                    live_count_7d INTEGER NOT NULL DEFAULT 0,
                    median_likes INTEGER NOT NULL DEFAULT 0,
                    creator_level INTEGER NOT NULL DEFAULT 0,
                    video_count INTEGER NOT NULL DEFAULT 0,
                    like_fan_ratio REAL NOT NULL DEFAULT 0,
                    settlement_range TEXT NOT NULL DEFAULT '',
                    settlement_min REAL NOT NULL DEFAULT 0,
                    settlement_max REAL NOT NULL DEFAULT 0,
                    settlement_mid REAL NOT NULL DEFAULT 0,
                    sales_per_fan REAL NOT NULL DEFAULT 0,
                    score REAL NOT NULL DEFAULT 0,
                    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self._ensure_additional_columns(conn)
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_influencers_category
                ON influencers(category)
                """
            )

    def _ensure_additional_columns(self, conn: sqlite3.Connection) -> None:
        existing_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(influencers)").fetchall()
        }
        for column, definition in ADDITIONAL_COLUMNS.items():
            if column not in existing_columns:
                conn.execute(f"ALTER TABLE influencers ADD COLUMN {column} {definition}")

    def upsert_influencers(self, rows: list[dict[str, Any]]) -> int:
        if not rows:
            return 0

        sql = """
            INSERT INTO influencers (
                nickname,
                profile_url,
                douyin_id,
                web_profile_url,
                fans,
                category,
                sales_30d,
                gmv_30d,
                product_count,
                live_count_7d,
                median_likes,
                creator_level,
                video_count,
                like_fan_ratio,
                settlement_range,
                settlement_min,
                settlement_max,
                settlement_mid,
                sales_per_fan,
                score,
                imported_at,
                updated_at
            )
            VALUES (
                :nickname,
                :profile_url,
                :douyin_id,
                :web_profile_url,
                :fans,
                :category,
                :sales_30d,
                :gmv_30d,
                :product_count,
                :live_count_7d,
                :median_likes,
                :creator_level,
                :video_count,
                :like_fan_ratio,
                :settlement_range,
                :settlement_min,
                :settlement_max,
                :settlement_mid,
                :sales_per_fan,
                :score,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT(profile_url) DO UPDATE SET
                nickname = excluded.nickname,
                douyin_id = excluded.douyin_id,
                web_profile_url = excluded.web_profile_url,
                fans = excluded.fans,
                category = excluded.category,
                sales_30d = excluded.sales_30d,
                gmv_30d = excluded.gmv_30d,
                product_count = excluded.product_count,
                live_count_7d = excluded.live_count_7d,
                median_likes = excluded.median_likes,
                creator_level = excluded.creator_level,
                video_count = excluded.video_count,
                like_fan_ratio = excluded.like_fan_ratio,
                settlement_range = excluded.settlement_range,
                settlement_min = excluded.settlement_min,
                settlement_max = excluded.settlement_max,
                settlement_mid = excluded.settlement_mid,
                sales_per_fan = excluded.sales_per_fan,
                score = excluded.score,
                updated_at = CURRENT_TIMESTAMP
        """
        with self.connect() as conn:
            conn.executemany(sql, rows)
        return len(rows)

    def replace_scores(self, scores: dict[str, float]) -> None:
        with self.connect() as conn:
            conn.executemany(
                """
                UPDATE influencers
                SET score = ?, updated_at = CURRENT_TIMESTAMP
                WHERE profile_url = ?
                """,
                [(score, profile_url) for profile_url, score in scores.items()],
            )

    def list_influencers(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    nickname,
                    profile_url,
                    douyin_id,
                    web_profile_url,
                    fans,
                    category,
                    sales_30d,
                    gmv_30d,
                    product_count,
                    live_count_7d,
                    median_likes,
                    creator_level,
                    video_count,
                    like_fan_ratio,
                    settlement_range,
                    settlement_min,
                    settlement_max,
                    settlement_mid,
                    sales_per_fan,
                    score,
                    imported_at,
                    updated_at
                FROM influencers
                ORDER BY score DESC, settlement_mid DESC, sales_30d DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.list_influencers())
