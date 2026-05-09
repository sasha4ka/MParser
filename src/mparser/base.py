import abc
from pathlib import Path
from typing import Any, Dict, Optional


class Parser_Registry:
    parsers: "Dict[str, Base_Parser]"
    config: Dict[str, Dict[str, Any]]

    def __init__(self, config: Optional[Dict[str, Dict[str, Any]]] = None):
        self.parsers = {}
        self.config = config if config is not None else {}

    def register_parser(self, parser_cls: type) -> None:
        parser_type = parser_cls.__name__
        config = self.config.get(parser_type)
        instance = parser_cls(config)
        self.parsers.update({parser_type: instance})

    def get_parser(self, file_path: Path) -> "Optional[Base_Parser]":
        for parser in self.parsers.values():
            if parser.match(file_path):
                return parser
        return None

    def list_parsers(self) -> "Dict[str, Base_Parser]":
        return self.parsers

    def __str__(self) -> str:
        return "Parser Registry:\n" + "\n".join(
            f"- {parser}" for parser in self.parsers.values()
        )


parser_registry = Parser_Registry()


class Base_Parser(abc.ABC):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config if config is not None else {}

    def __init_subclass__(cls, **kwargs: Dict[str, Any]) -> None:
        super().__init_subclass__(**kwargs)

        if not cls.__name__.startswith("Base"):
            parser_registry.register_parser(cls)

    @abc.abstractmethod
    def process(self, file_path: Path) -> Any:
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    def match(self, file_path: Path) -> bool:
        raise NotImplementedError("This method should be implemented by subclasses.")

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return self.name


class Parsing_Exception(Exception):
    pass
