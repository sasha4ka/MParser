from pathlib import Path  # noqa: I001
from sys import argv

import json
from typing import Optional

from mparser.base import Table, parser_registry
from mparser.base import table_registry
import mparser.parsers  # type: ignore # noqa I001
import mparser.tables  # type: ignore # noqa I001


def show_registry() -> bool:
    return "-r" in argv


def get_files() -> list[Path]:
    if "-f" in argv:
        i = argv.index("-f")
        if i + 1 == len("argv"):
            print("no file specified")
            return []
        text_path = argv[i + 1]
        try:
            return [Path(text_path)]
        except TypeError:
            print("Wrong path format")
            return []

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

    if not Path.exists(Path("files.json")):
        print("no files.json or -f found. Enter paths (enter for done):")
        files = []
        i = 0
        while True:
            text_path = input(f"{i}: ")
            if not text_path:
                break
            try:
                path = Path(text_path)
                files.append(path)
            except TypeError:
                continue
            i += 1
        return files

    print("WIP")
    return []


def get_table() -> Optional[Table]:
    if "-t" in argv:
        i = argv.index("-t")
        if i + 1 == len(argv):
            print("no table specified")
            return None
        table_name = argv[i + 1]
        table = table_registry.create_table(table_name)
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

    if show_registry():
        print(parser_registry)
        print(table_registry)
        return

    files = get_files()
    if not files:
        print("no files given. exiting...")
        return
    table = get_table()
    if not table:
        print("no table given. exiting...")
        return

    for file in files:
        parser = parser_registry.get_parser(file)
        if not parser:
            print(f"parser not found for {file}")
            continue
        table.parse_rows(parser.process(file))

    print(table)


if __name__ == "__main__":
    main()
