from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

from app.config import DADADUO_COLUMNS, NUMERIC_COLUMNS, REQUIRED_COLUMNS
from app.db import Database
from app.scoring import calculate_sales_per_fan, calculate_scores


DDD_COLUMNS = {
    "达人名称": "nickname",
    "达人抖音id": "douyin_id",
    "粉丝总量": "fans",
    "平均获赞数": "median_likes",
    "推广商品数": "product_count",
}


DDD_OPTIONAL_COLUMNS = {
    "带货等级": "creator_level",
    "视频数": "video_count",
    "平均赞粉比": "like_fan_ratio",
    "预估结算金额": "settlement_range",
}


WEB_PROFILE_URL_COLUMNS = [
    "web_profile_url",
    "profile_url",
    "抖音主页",
    "达人主页",
    "主页链接",
    "主页",
]


def _parse_like_fan_ratio(value: object) -> float:
    if pd.isna(value):
        return 0.0
    text = str(value).strip()
    if not text:
        return 0.0

    has_percent = text.endswith("%")
    text = text.rstrip("%").strip()
    parsed = pd.to_numeric(text, errors="coerce")
    if pd.isna(parsed):
        return 0.0

    ratio = float(parsed)
    if has_percent or ratio > 1:
        ratio /= 100
    return round(max(ratio, 0.0), 4)


def _parse_settlement_amount(value: object) -> float:
    if pd.isna(value):
        return 0.0
    text = str(value).strip().lower().replace(",", "")
    if not text:
        return 0.0

    multiplier = 1.0
    if text.endswith(("w", "万")):
        multiplier = 10000.0
        text = text[:-1]

    parsed = pd.to_numeric(text, errors="coerce")
    if pd.isna(parsed):
        return 0.0
    return max(float(parsed) * multiplier, 0.0)


def _parse_settlement_range(value: object) -> tuple[str, float, float, float]:
    if pd.isna(value):
        return "", 0.0, 0.0, 0.0

    text = str(value).strip()
    if not text:
        return "", 0.0, 0.0, 0.0

    parts = [part.strip() for part in re.split(r"[~\-–—]", text) if part.strip()]
    if len(parts) == 1:
        minimum = maximum = _parse_settlement_amount(parts[0])
    else:
        minimum = _parse_settlement_amount(parts[0])
        maximum = _parse_settlement_amount(parts[-1])

    if maximum < minimum:
        minimum, maximum = maximum, minimum
    midpoint = (minimum + maximum) / 2 if maximum or minimum else 0.0
    return text, minimum, maximum, midpoint


def _read_source(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("Only CSV and Excel files are supported")


def _normalize_standard_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        joined = ", ".join(missing_columns)
        raise ValueError(f"CSV missing required columns: {joined}")
    normalized = df[REQUIRED_COLUMNS].copy()
    for column in DADADUO_COLUMNS:
        if column in df.columns:
            normalized[column] = df[column]
        else:
            normalized[column] = "" if column in {"douyin_id", "web_profile_url", "settlement_range"} else 0
    return normalized[REQUIRED_COLUMNS + DADADUO_COLUMNS]


def _normalize_dadaduo_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [column for column in DDD_COLUMNS if column not in df.columns]
    if missing_columns:
        joined = ", ".join(missing_columns)
        raise ValueError(f"Excel missing required Dadaduo columns: {joined}")

    normalized = pd.DataFrame()
    normalized["nickname"] = df["达人名称"]
    douyin_id = df["达人抖音id"].fillna("").astype(str).str.strip()
    settlement_ranges = df.get("预估结算金额", pd.Series("", index=df.index)).apply(
        _parse_settlement_range
    )

    normalized["profile_url"] = "dadaduo://douyin/" + douyin_id
    normalized["douyin_id"] = douyin_id
    normalized["web_profile_url"] = ""
    for column in WEB_PROFILE_URL_COLUMNS:
        if column in df.columns and column != "profile_url":
            imported_urls = df[column].fillna("").astype(str).str.strip()
            normalized["web_profile_url"] = imported_urls.where(
                imported_urls != "", normalized["web_profile_url"]
            )
            break
    normalized["fans"] = df["粉丝总量"]
    normalized["category"] = "dadaduo"
    normalized["sales_30d"] = 0
    normalized["gmv_30d"] = 0.0
    normalized["product_count"] = df["推广商品数"]
    normalized["live_count_7d"] = 0
    normalized["median_likes"] = df["平均获赞数"]
    normalized["creator_level"] = df.get("带货等级", 0)
    normalized["video_count"] = df.get("视频数", 0)
    normalized["like_fan_ratio"] = df.get(
        "平均赞粉比", pd.Series(0, index=df.index)
    ).apply(_parse_like_fan_ratio)
    normalized["settlement_range"] = settlement_ranges.apply(lambda item: item[0])
    normalized["settlement_min"] = settlement_ranges.apply(lambda item: item[1])
    normalized["settlement_max"] = settlement_ranges.apply(lambda item: item[2])
    normalized["settlement_mid"] = settlement_ranges.apply(lambda item: item[3])
    return normalized[REQUIRED_COLUMNS + DADADUO_COLUMNS]


def _normalize_input_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if all(column in df.columns for column in REQUIRED_COLUMNS):
        return _normalize_standard_dataframe(df)
    if all(column in df.columns for column in DDD_COLUMNS):
        return _normalize_dadaduo_dataframe(df)

    required = ", ".join(REQUIRED_COLUMNS)
    dadaduo = ", ".join(DDD_COLUMNS)
    raise ValueError(
        "Input file must contain either standard columns "
        f"({required}) or Dadaduo columns ({dadaduo})"
    )


def load_csv(csv_path: Path) -> pd.DataFrame:
    path = Path(csv_path)
    df = _normalize_input_dataframe(_read_source(path))
    df["nickname"] = df["nickname"].fillna("").astype(str).str.strip()
    df["profile_url"] = df["profile_url"].fillna("").astype(str).str.strip()
    df["category"] = df["category"].fillna("").astype(str).str.strip()
    df["douyin_id"] = df["douyin_id"].fillna("").astype(str).str.strip()
    df["web_profile_url"] = df["web_profile_url"].fillna("").astype(str).str.strip()
    df["settlement_range"] = df["settlement_range"].fillna("").astype(str).str.strip()
    df = df[df["profile_url"] != ""]

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    integer_columns = [
        "fans",
        "sales_30d",
        "product_count",
        "live_count_7d",
        "median_likes",
        "creator_level",
        "video_count",
    ]
    for column in integer_columns:
        df[column] = df[column].clip(lower=0).round().astype(int)
    df["gmv_30d"] = df["gmv_30d"].clip(lower=0).astype(float)
    df["like_fan_ratio"] = df["like_fan_ratio"].clip(lower=0).astype(float)
    df["settlement_min"] = df["settlement_min"].clip(lower=0).astype(float)
    df["settlement_max"] = df["settlement_max"].clip(lower=0).astype(float)
    df["settlement_mid"] = df["settlement_mid"].clip(lower=0).astype(float)

    df["sales_per_fan"] = df.apply(
        lambda row: calculate_sales_per_fan(row["sales_30d"], row["fans"]),
        axis=1,
    )
    df["score"] = 0.0
    return df.drop_duplicates(subset=["profile_url"], keep="last")


def recalculate_all_scores(db: Database) -> None:
    df = db.to_dataframe()
    if df.empty:
        return
    df["score"] = calculate_scores(df)
    scores = dict(zip(df["profile_url"], df["score"]))
    db.replace_scores(scores)


def import_csv(db: Database, csv_path: Path) -> int:
    db.init_schema()
    df = load_csv(csv_path)
    imported_count = db.upsert_influencers(df.to_dict(orient="records"))
    recalculate_all_scores(db)
    return imported_count
