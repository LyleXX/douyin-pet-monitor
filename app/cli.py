from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from app.config import DB_PATH, EXPORT_DIR
from app.db import Database
from app.exporter import export_dataframe_to_excel, write_dataframe_to_excel
from app.filtering import filter_creators
from app.importer import import_csv


def _records_to_jsonable(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    return json.loads(df.to_json(orient="records", date_format="iso"))


def _emit(payload: Any) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="douyin-backend")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List all creator records")
    list_parser.add_argument("--db", type=Path, default=DB_PATH)

    import_parser = subparsers.add_parser("import-csv", help="Import a CSV file")
    import_parser.add_argument("--db", type=Path, default=DB_PATH)
    import_parser.add_argument("--csv", type=Path, required=True)

    export_parser = subparsers.add_parser("export-excel", help="Export current ranking to Excel")
    export_parser.add_argument("--db", type=Path, default=DB_PATH)
    export_parser.add_argument("--output", type=Path, required=False)
    export_parser.add_argument("--fans-min", type=int, required=False)
    export_parser.add_argument("--fans-max", type=int, required=False)
    export_parser.add_argument("--sales-min", type=int, required=False)
    export_parser.add_argument("--sales-max", type=int, required=False)
    export_parser.add_argument("--creator-level-min", type=int, required=False)
    export_parser.add_argument("--creator-level-max", type=int, required=False)
    export_parser.add_argument("--product-count-min", type=int, required=False)
    export_parser.add_argument("--product-count-max", type=int, required=False)
    export_parser.add_argument("--like-fan-ratio-min", type=float, required=False)
    export_parser.add_argument("--like-fan-ratio-max", type=float, required=False)
    export_parser.add_argument("--settlement-min", type=float, required=False)
    export_parser.add_argument("--settlement-max", type=float, required=False)
    export_parser.add_argument("--category", action="append", default=[])

    return parser


def handle_list(db: Database) -> list[dict[str, Any]]:
    return _records_to_jsonable(db.to_dataframe())


def handle_import(db: Database, csv_path: Path) -> dict[str, Any]:
    imported = import_csv(db, csv_path)
    records = handle_list(db)
    return {"imported": imported, "total": len(records), "records": records}


def handle_export(
    db: Database,
    output_path: Path | None,
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
    categories: list[str] | None = None,
) -> dict[str, Any]:
    df = filter_creators(
        db.to_dataframe(),
        fans_min=fans_min,
        fans_max=fans_max,
        sales_min=sales_min,
        sales_max=sales_max,
        creator_level_min=creator_level_min,
        creator_level_max=creator_level_max,
        product_count_min=product_count_min,
        product_count_max=product_count_max,
        like_fan_ratio_min=like_fan_ratio_min,
        like_fan_ratio_max=like_fan_ratio_max,
        settlement_min=settlement_min,
        settlement_max=settlement_max,
        categories=categories,
    )
    if output_path is None:
        output = export_dataframe_to_excel(df, EXPORT_DIR)
    else:
        output = write_dataframe_to_excel(df, output_path)
    return {"output_path": str(output), "rows": len(df)}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    db = Database(args.db)
    db.init_schema()

    if args.command == "list":
        _emit(handle_list(db))
        return 0

    if args.command == "import-csv":
        _emit(handle_import(db, args.csv))
        return 0

    if args.command == "export-excel":
        _emit(
            handle_export(
                db,
                args.output,
                fans_min=args.fans_min,
                fans_max=args.fans_max,
                sales_min=args.sales_min,
                sales_max=args.sales_max,
                creator_level_min=args.creator_level_min,
                creator_level_max=args.creator_level_max,
                product_count_min=args.product_count_min,
                product_count_max=args.product_count_max,
                like_fan_ratio_min=args.like_fan_ratio_min,
                like_fan_ratio_max=args.like_fan_ratio_max,
                settlement_min=args.settlement_min,
                settlement_max=args.settlement_max,
                categories=args.category,
            )
        )
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
