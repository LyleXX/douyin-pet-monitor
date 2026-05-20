from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def filter_creators(
    df: pd.DataFrame,
    *,
    fans_min: int | None = None,
    fans_max: int | None = None,
    sales_min: int | None = None,
    sales_max: int | None = None,
    creator_level_min: int | None = None,
    creator_level_max: int | None = None,
    product_count_min: int | None = None,
    product_count_max: int | None = None,
    like_fan_ratio_min: float | None = None,
    like_fan_ratio_max: float | None = None,
    settlement_min: float | None = None,
    settlement_max: float | None = None,
    categories: Sequence[str] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()

    if fans_min is not None:
        filtered = filtered[filtered["fans"] >= fans_min]
    if fans_max is not None:
        filtered = filtered[filtered["fans"] <= fans_max]
    if sales_min is not None:
        filtered = filtered[filtered["sales_30d"] >= sales_min]
    if sales_max is not None:
        filtered = filtered[filtered["sales_30d"] <= sales_max]
    if creator_level_min is not None and "creator_level" in filtered.columns:
        filtered = filtered[filtered["creator_level"] >= creator_level_min]
    if creator_level_max is not None and "creator_level" in filtered.columns:
        filtered = filtered[filtered["creator_level"] <= creator_level_max]
    if product_count_min is not None:
        filtered = filtered[filtered["product_count"] >= product_count_min]
    if product_count_max is not None:
        filtered = filtered[filtered["product_count"] <= product_count_max]
    if like_fan_ratio_min is not None and "like_fan_ratio" in filtered.columns:
        filtered = filtered[filtered["like_fan_ratio"] >= like_fan_ratio_min]
    if like_fan_ratio_max is not None and "like_fan_ratio" in filtered.columns:
        filtered = filtered[filtered["like_fan_ratio"] <= like_fan_ratio_max]
    if settlement_min is not None and "settlement_mid" in filtered.columns:
        filtered = filtered[filtered["settlement_mid"] >= settlement_min]
    if settlement_max is not None and "settlement_mid" in filtered.columns:
        filtered = filtered[filtered["settlement_mid"] <= settlement_max]

    if categories:
        normalized = [category for category in categories if category]
        if normalized:
            filtered = filtered[filtered["category"].isin(normalized)]

    return filtered
