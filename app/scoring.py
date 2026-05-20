from __future__ import annotations

import pandas as pd


GENERIC_SCORE_WEIGHTS = {
    "sales_per_fan": 0.35,
    "sales_30d": 0.25,
    "gmv_30d": 0.15,
    "median_likes": 0.10,
    "live_count_7d": 0.10,
    "product_count": 0.05,
}


DADADUO_SCORE_WEIGHTS = {
    "settlement_mid": 0.30,
    "creator_level": 0.20,
    "video_count": 0.15,
    "like_fan_ratio": 0.15,
    "median_likes": 0.10,
    "product_count": 0.10,
}


def calculate_sales_per_fan(sales_30d: float, fans: float) -> float:
    if fans <= 0:
        return 0.0
    return float(sales_30d) / float(fans)


def _weighted_score(df: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)

    weighted_score = pd.Series(0.0, index=df.index)
    for column, weight in weights.items():
        if column not in df.columns:
            continue
        values = pd.to_numeric(df[column], errors="coerce").fillna(0.0)
        min_value = values.min()
        max_value = values.max()
        if max_value == min_value:
            normalized = pd.Series(0.0, index=df.index)
        else:
            normalized = (values - min_value) / (max_value - min_value)
        weighted_score += normalized * weight

    return (weighted_score * 100).round(2)


def calculate_scores(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)

    scores = _weighted_score(df, GENERIC_SCORE_WEIGHTS)

    if "category" in df.columns:
        dadaduo_mask = df["category"].astype(str).eq("dadaduo")
        if dadaduo_mask.any():
            scores.loc[dadaduo_mask] = _weighted_score(
                df.loc[dadaduo_mask], DADADUO_SCORE_WEIGHTS
            )

    return scores.round(2)
