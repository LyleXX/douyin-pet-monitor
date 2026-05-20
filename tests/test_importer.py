from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.db import Database
from app.importer import import_csv


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


def make_csv(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows, columns=REQUIRED_COLUMNS).to_csv(path, index=False)


def test_import_and_upsert_and_sales_per_fan(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    csv1 = tmp_path / "batch1.csv"
    csv2 = tmp_path / "batch2.csv"

    make_csv(
        csv1,
        [
            {
                "nickname": "A",
                "profile_url": "https://example.com/a",
                "fans": 100,
                "category": "pet",
                "sales_30d": 50,
                "gmv_30d": 500,
                "product_count": 10,
                "live_count_7d": 2,
                "median_likes": 20,
            },
            {
                "nickname": "B",
                "profile_url": "https://example.com/b",
                "fans": 200,
                "category": "pet",
                "sales_30d": 80,
                "gmv_30d": 1000,
                "product_count": 8,
                "live_count_7d": 3,
                "median_likes": 30,
            },
        ],
    )

    make_csv(
        csv2,
        [
            {
                "nickname": "A2",
                "profile_url": "https://example.com/a",
                "fans": 100,
                "category": "pet-food",
                "sales_30d": 90,
                "gmv_30d": 900,
                "product_count": 12,
                "live_count_7d": 4,
                "median_likes": 25,
            }
        ],
    )

    db = Database(db_path)
    db.init_schema()

    import_csv(db, csv1)
    rows = db.list_influencers()
    assert len(rows) == 2

    row_a = next(r for r in rows if r["profile_url"] == "https://example.com/a")
    assert row_a["sales_per_fan"] == 0.5

    import_csv(db, csv2)
    rows = db.list_influencers()
    assert len(rows) == 2

    row_a = next(r for r in rows if r["profile_url"] == "https://example.com/a")
    assert row_a["nickname"] == "A2"
    assert row_a["category"] == "pet-food"
    assert row_a["sales_30d"] == 90
    assert row_a["sales_per_fan"] == 0.9


def test_score_is_computed_after_import(tmp_path: Path) -> None:
    db_path = tmp_path / "test_score.db"
    csv1 = tmp_path / "batch.csv"

    make_csv(
        csv1,
        [
            {
                "nickname": "low",
                "profile_url": "https://example.com/low",
                "fans": 1000,
                "category": "pet",
                "sales_30d": 10,
                "gmv_30d": 100,
                "product_count": 1,
                "live_count_7d": 1,
                "median_likes": 5,
            },
            {
                "nickname": "high",
                "profile_url": "https://example.com/high",
                "fans": 1000,
                "category": "pet",
                "sales_30d": 100,
                "gmv_30d": 1000,
                "product_count": 10,
                "live_count_7d": 6,
                "median_likes": 80,
            },
        ],
    )

    db = Database(db_path)
    db.init_schema()
    import_csv(db, csv1)

    rows = db.list_influencers()
    low = next(r for r in rows if r["nickname"] == "low")
    high = next(r for r in rows if r["nickname"] == "high")

    assert 0 <= low["score"] <= 100
    assert 0 <= high["score"] <= 100
    assert high["score"] > low["score"]


def test_single_row_import_has_zero_score_without_crashing(tmp_path: Path) -> None:
    db_path = tmp_path / "single.db"
    csv1 = tmp_path / "single.csv"

    make_csv(
        csv1,
        [
            {
                "nickname": "solo",
                "profile_url": "https://example.com/solo",
                "fans": 100,
                "category": "pet",
                "sales_30d": 10,
                "gmv_30d": 100,
                "product_count": 1,
                "live_count_7d": 1,
                "median_likes": 5,
            }
        ],
    )

    db = Database(db_path)
    db.init_schema()
    import_csv(db, csv1)

    rows = db.list_influencers()
    assert len(rows) == 1
    assert rows[0]["score"] == 0.0


def test_import_dadaduo_xlsx_maps_columns(tmp_path: Path) -> None:
    db_path = tmp_path / "dadaduo.db"
    xlsx_path = tmp_path / "dadaduo.xlsx"

    pd.DataFrame(
        [
            {
                "达人名称": "官官",
                "达人抖音id": "ManyueDanta",
                "带货等级": 2,
                "视频数": 112,
                "粉丝总量": 9614,
                "平均获赞数": 316,
                "平均赞粉比": "3.29%",
                "推广商品数": 34,
                "预估结算金额": "10w~50w",
            }
        ]
    ).to_excel(xlsx_path, index=False)

    db = Database(db_path)
    db.init_schema()
    import_csv(db, xlsx_path)

    rows = db.list_influencers()
    assert len(rows) == 1
    assert rows[0]["nickname"] == "官官"
    assert rows[0]["profile_url"] == "dadaduo://douyin/ManyueDanta"
    assert rows[0]["fans"] == 9614
    assert rows[0]["category"] == "dadaduo"
    assert rows[0]["sales_30d"] == 0
    assert rows[0]["gmv_30d"] == 0
    assert rows[0]["product_count"] == 34
    assert rows[0]["median_likes"] == 316


def test_import_dadaduo_xlsx_preserves_enriched_columns_and_scores(tmp_path: Path) -> None:
    db_path = tmp_path / "dadaduo_enriched.db"
    xlsx_path = tmp_path / "dadaduo_enriched.xlsx"

    pd.DataFrame(
        [
            {
                "达人名称": "波妞儿是老大",
                "达人抖音id": "79504609738",
                "带货等级": 2,
                "视频数": 10,
                "粉丝总量": 1000,
                "平均获赞数": 10,
                "平均赞粉比": "1.00%",
                "推广商品数": 1,
                "预估结算金额": "0~250",
            },
            {
                "达人名称": "high",
                "达人抖音id": "high-id",
                "带货等级": 5,
                "视频数": 120,
                "粉丝总量": 9000,
                "平均获赞数": 600,
                "平均赞粉比": "6.67%",
                "推广商品数": 30,
                "预估结算金额": "10w~50w",
            },
        ]
    ).to_excel(xlsx_path, index=False)

    db = Database(db_path)
    db.init_schema()
    import_csv(db, xlsx_path)

    rows = db.list_influencers()
    low = next(row for row in rows if row["nickname"] == "波妞儿是老大")
    high = next(row for row in rows if row["nickname"] == "high")

    assert low["douyin_id"] == "79504609738"
    assert low["web_profile_url"] == ""
    assert low["creator_level"] == 2
    assert low["video_count"] == 10
    assert low["like_fan_ratio"] == 0.01
    assert low["settlement_range"] == "0~250"
    assert low["settlement_min"] == 0
    assert low["settlement_max"] == 250
    assert low["settlement_mid"] == 125

    assert high["douyin_id"] == "high-id"
    assert high["creator_level"] == 5
    assert high["video_count"] == 120
    assert high["like_fan_ratio"] == 0.0667
    assert high["settlement_range"] == "10w~50w"
    assert high["settlement_min"] == 100000
    assert high["settlement_max"] == 500000
    assert high["settlement_mid"] == 300000
    assert high["score"] > low["score"]
