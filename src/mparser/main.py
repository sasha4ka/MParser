from pathlib import Path  # noqa: I001
from sys import argv
from typing import Optional

from mparser.base import parser_registry
import mparser.parsers  # noqa I001


def parse_file_path() -> Optional[Path]:
    for i in range(len(argv)):
        if argv[i] in ["-f", "--file"]:
            if i + 1 == len(argv):
                return None
            return Path(argv[i + 1])
    return None


def main() -> None:
    print("MParser v0.1.0")
    print(parser_registry)
    print("-" * 40)

    file_path = parse_file_path()
    if not file_path:
        print("Not file path given. Exiting...")
        return

    parser = parser_registry.get_parser(file_path)
    if not parser:
        print("Unknown file type. Exiting...")
        return

    print(f"Selected parser: {parser.name}")
    result = parser.process(file_path)
    print("Parsing results:")
    print(result)


if __name__ == "__main__":
    main()
