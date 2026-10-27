"""Suivi du stock : lecture d'un export CSV, requetes parametrees, archivage par un outil externe."""
from __future__ import annotations

import csv
import logging
import os
import sqlite3
import subprocess
from dataclasses import dataclass
from typing import Dict, Iterable, List

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class Item:
    sku: str
    quantity: int


def read_export(path: str) -> List[Item]:
    items = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            items.append(Item(sku=row["sku"], quantity=int(row["quantity"])))
    return items


def save(connection: sqlite3.Connection, items: Iterable[Item]) -> None:
    connection.executemany(
        "INSERT INTO stock(sku, quantity) VALUES (?, ?) "
        "ON CONFLICT(sku) DO UPDATE SET quantity = excluded.quantity",
        [(item.sku, item.quantity) for item in items],
    )


def quantities_by_sku(connection: sqlite3.Connection, skus: List[str]) -> Dict[str, int]:
    placeholders = ", ".join("?" for _ in skus)
    query = "SELECT sku, quantity FROM stock WHERE sku IN (" + placeholders + ")"
    return dict(connection.execute(query, skus).fetchall())


def average_quantity(items: List[Item]) -> float:
    if not items:
        return 0.0
    return sum(item.quantity for item in items) / len(items)


def archive(folder: str, target: str) -> bool:
    try:
        subprocess.run(["tar", "-czf", target, "-C", folder, "."], check=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as error:
        LOG.warning("archive of %s failed: %s", folder, error)
        return False
    return True


def database_path() -> str:
    return os.environ.get("STOCK_DB", "stock.sqlite3")
