from pathlib import Path  # noqa: I001
import json
import argparse
from itertools import count
from typing import Optional

from mparser.base import Table, parser_registry
from mparser.base import table_registry
import mparser.parsers  # type: ignore # noqa I001
import mparser.tables  # type: ignore # noqa I001


def get_files(args: argparse.Namespace) -> list[Path]:
    if args.file:
        return [Path(args.file)]

    if Path.exists(Path("files.json")):
        data: list[str] = []
        try:
            with open("files.json", "r") as file:
                data = json.load(file)

        except json.JSONDecodeError:
            print("unknown files.json format")
            return []
        files: list[Path] = []
        for text_path in data:
            try:
                files.append(Path(text_path))
            except TypeError:
                print(f"wrong path format: {text_path} from files.json. Skipping...")
        print(f"using {len(files)} files from files.json")
        return files

    print("no files.json or -f found. Enter paths (enter for done):")
    files = []
    for i in count(start=0, step=1):
        text_path = input(f"{i}: ")
        if not text_path:
            break
        try:
            files.append(Path(text_path))
        except TypeError:
            continue
    return files


def get_table(args: argparse.Namespace) -> Optional[Table]:
    if args.table:
        table = table_registry.create_table(args.table)
        if not table:
            print("table not found")
            return None
        return table

    print("-" * 30)
    print(table_registry)
    print()
    while True:
        table_name = input("table: ")
        table = table_registry.create_table(table_name)
        if table:
            return table
        print("table not found. try again")


def main() -> None:
    print("MParser v0.1.0")

    parser = argparse.ArgumentParser(
        prog="MParser",
        description="Module parser for different filetypes and data schemes",
    )
    parser.add_argument(
        "-r", "--registry", help="show table and parser registry", action="store_true"
    )
    parser.add_argument("-f", "--file", help="select file for parsing")
    parser.add_argument("-t", "--table", help="select table for parsing")
    parser.add_argument(
        "-s", "--short", help="dont show table rows", action="store_true"
    )

    args = parser.parse_args()

    if args.registry:
        print(parser_registry)
        print(table_registry)
        return

    files = get_files(args)
    if not files:
        print("no table given. exiting...")
        return

    table = get_table(args)
    if not table:
        print("no table given. exiting...")
        return

    for file in files:
        parser = parser_registry.get_parser(file)
        if not parser:
            print(f"parser not found for {file}")
            continue
        table.parse_rows(parser.process(file))

    if not args.short:
        print(table)


if __name__ == "__main__":
    main()
