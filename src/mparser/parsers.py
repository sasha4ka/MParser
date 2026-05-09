from collections import deque
from pathlib import Path
from typing import Any, Deque, Dict, Iterator, List, Optional, TextIO

from mparser.base import Base_Parser, Parsing_Exception


def read_by_char(stream: TextIO) -> Iterator[tuple[int, int, Optional[str]]]:
    for ln, line in enumerate(stream, start=0):
        if not line:
            yield ln, 0, None
        for cn, c in enumerate(line, start=0):
            yield ln, cn, c


class JSON_Parser(Base_Parser):
    class Char_Iterator:
        def __init__(self, stream: TextIO):
            self._file = stream
            self._stream = read_by_char(stream)
            self._q: Deque[str] = deque([])
            self._blank_skip = True

        def _next(self) -> Optional[str]:
            if self._q:
                return self._q.popleft()
            self._l, self._c, c = self._stream.__next__()
            return c

        def __next__(self) -> Optional[str]:
            if not self._blank_skip:
                return self._next()
            while c := self._next():
                if c not in [" ", "\t", "\n"]:
                    return c
            return None

        def return_char(self, c: str) -> None:
            self._q.append(c)

        def current(self) -> tuple[int, int]:
            return self._l, self._c

        def __iter__(self) -> "JSON_Parser.Char_Iterator":
            return self

        def set_blank_skip(self, blank_skip: bool) -> None:
            self._blank_skip = blank_skip

    class JSON_Parsing_Exception(Parsing_Exception):
        def __init__(
            self,
            stream: "Optional[JSON_Parser.Char_Iterator]" = None,
            *args: list[Any],
            **kwargs: Dict[str, Any],
        ):
            if stream:
                line_n, char_n = stream.current()
                text = f"Invalid JSON format at {line_n}:{char_n}"
                super().__init__(self, text, *args, **kwargs)
            super().__init__(self, *args, **kwargs)

    def process(self, file_path: Path) -> Any:
        with open(file_path, "r") as file:
            stream = self.Char_Iterator(file)
            obj = self.parse_value(stream, stop=[], is_root=True)
            return obj

    def parse_value(
        self, stream: Char_Iterator, stop: List[str], is_root: bool = False
    ) -> Any:
        first = stream.__next__()
        if not first:
            raise self.JSON_Parsing_Exception(stream)
        stream.return_char(first)
        if first == "{":
            return self.parse_object(stream)
        elif first == "[":
            return self.parse_list(stream)
        elif is_root:
            raise self.JSON_Parsing_Exception(stream)
        elif first == '"':
            return self.parse_string(stream)
        else:
            return self.parse_num(stream, stop)

    def parse_object(self, stream: Char_Iterator) -> Dict[str, Any]:
        if stream.__next__() != "{":
            raise self.JSON_Parsing_Exception(stream)

        obj: Dict[str, Any] = {}
        while True:
            key = self.parse_string(stream)
            if stream.__next__() != ":":
                raise self.JSON_Parsing_Exception(stream)
            value = self.parse_value(stream, stop=["}", ","])
            obj[key] = value

            c = stream.__next__()
            if c == "}":
                break
            elif c == ",":
                continue
            else:
                raise self.JSON_Parsing_Exception(stream)
        return obj

    def parse_list(self, stream: Char_Iterator) -> List[Any]:
        if stream.__next__() != "[":
            raise self.JSON_Parsing_Exception(stream)

        list: List[Any] = []
        while True:
            val = self.parse_value(stream, stop=["]", ","])
            list.append(val)

            c = stream.__next__()
            if c == "]":
                break
            elif c == ",":
                continue
            else:
                raise self.JSON_Parsing_Exception(stream)
        return list

    def parse_string(self, stream: Char_Iterator) -> str:
        if stream.__next__() != '"':
            raise self.JSON_Parsing_Exception(stream)
        s = ""
        stream.set_blank_skip(False)
        for c in stream:
            if not c:
                raise self.JSON_Parsing_Exception(stream)
            if c == '"':
                break
            s = s + c
        stream.set_blank_skip(True)
        return s

    def parse_num(self, stream: Char_Iterator, stop: List[str]) -> int | float:
        word = ""
        for c in stream:
            if c in stop:
                stream.return_char(c)
                break
            if not c:
                raise self.JSON_Parsing_Exception(stream)
            word = word + c
        try:
            return int(word)
        except ValueError:
            pass

        return float(word)

    def match(self, file_path: Path) -> bool:
        return file_path.suffix == ".json"


class XML_Parser(Base_Parser):
    def process(self, file_path: Path) -> Dict[str, Any]:
        return {"key": "value"}

    def match(self, file_path: Path) -> bool:
        return file_path.suffix == ".xml"
