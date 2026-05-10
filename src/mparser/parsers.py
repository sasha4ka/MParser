import csv
from pathlib import Path

from mparser.base import Base_Parser


class CSV_Parser(Base_Parser):
    def process(self, file_path: Path) -> list[list[str]]:
        csv_config = getattr(self, "config", {}) or {}
        delimiter = csv_config.get("delimiter", ",")
        quotechar = csv_config.get("quotechar", '"')
        escapechar = csv_config.get("escapechar")
        has_header = csv_config.get("has_header", False)

        with open(file_path, "r", newline="", encoding="utf-8") as file:
            if has_header:
                file.readline()
            return [
                row
                for row in csv.reader(
                    file,
                    delimiter=delimiter,
                    quotechar=quotechar,
                    escapechar=escapechar,
                )
            ]

    def match(self, file_path: Path) -> bool:
        return file_path.suffix == ".csv"
