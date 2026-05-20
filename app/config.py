from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "douyin_creators.db"
EXPORT_DIR = BASE_DIR / "exports"


REQUIRED_COLUMNS = [
    "nickname",
    "profile_url",
    "fans",
    "category",
    "sales_30d",
    "gmv_30d",
    "product_count",
    "live_count_7d",
    "median_likes",
]


DADADUO_COLUMNS = [
    "douyin_id",
    "web_profile_url",
    "creator_level",
    "video_count",
    "like_fan_ratio",
    "settlement_range",
    "settlement_min",
    "settlement_max",
    "settlement_mid",
]


NUMERIC_COLUMNS = [
    "fans",
    "sales_30d",
    "gmv_30d",
    "product_count",
    "live_count_7d",
    "median_likes",
    "creator_level",
    "video_count",
    "like_fan_ratio",
    "settlement_min",
    "settlement_max",
    "settlement_mid",
]
