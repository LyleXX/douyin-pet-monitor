from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config import EXPORT_DIR


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    from io import BytesIO

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="creators")
    return buffer.getvalue()


def write_dataframe_to_excel(df: pd.DataFrame, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="creators")
    return output_path


def export_dataframe_to_excel(df: pd.DataFrame, export_dir: Path = EXPORT_DIR) -> Path:
    from datetime import datetime

    export_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = export_dir / f"douyin_creator_ranking_{timestamp}.xlsx"
    return write_dataframe_to_excel(df, output_path)
