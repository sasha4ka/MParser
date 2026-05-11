import abc
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple


class Parser_Registry:
    """A registry of all parsers"""

    parsers: "Dict[str, Base_Parser]"
    config: Dict[str, Dict[str, Any]]

    def __init__(self, config: Optional[Dict[str, Dict[str, Any]]] = None):
        self.parsers = {}
        self.config = config or {}

    def register_parser(self, parser_cls: type) -> None:
        """Create and register an instance of parser class"""
        parser_type = parser_cls.__name__
        config = self.config.get(parser_type)
        instance = parser_cls(config)
        self.parsers.update({parser_type: instance})

    def get_parser(self, file_path: Path) -> "Optional[Base_Parser]":
        """Get parser by file extension"""
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
    """Abstract parser"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config if config is not None else {}

    def __init_subclass__(cls, **kwargs: Dict[str, Any]) -> None:
        super().__init_subclass__(**kwargs)

        if not cls.__name__.startswith("Base"):
            parser_registry.register_parser(cls)

    @abc.abstractmethod
    def process(self, file_path: Path) -> list[list[str]]:
        """Parse a file"""
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    def match(self, file_path: Path) -> bool:
        """Returns true if parser can be applyed to this file"""
        raise NotImplementedError("This method should be implemented by subclasses.")

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return self.name


class Row:
    """Contains values from one row. \
Values can be obtained by column's name (row.title, row.cost)"""

    table: "Table"

    def __init__(
        self,
        table: "Table",
        columns: "list[Column]",
    ) -> None:
        self.table = table
        self._columns = columns

        for column in columns:
            self.__dict__[column.name] = None

    def __str__(self) -> str:
        return "; ".join(str(self.__dict__[column.name]) for column in self._columns)


class Column(abc.ABC):
    """(Abstract) Declares a column in table"""

    name: str
    data_type: type


class Main_Column(Column):
    def __init__(self, *, name: Optional[str] = None, data_type: type) -> None:
        self.name = name or "_not_given"
        self.data_type = data_type


class Calc_Column(Column):
    calc: Callable[[Row], Any]

    def __init__(
        self, *, name: Optional[str] = None, data_type: type, calc: Callable[[Row], Any]
    ):
        self.name = name or "_not_given"
        self.data_type = data_type
        self.calc = calc


def Calculation(data_type: type, name: Optional[str] = None) -> Any:
    def decorator(func: Callable[[Row], Any]) -> Calc_Column:
        return Calc_Column(name=name, data_type=data_type, calc=func)

    return decorator


class Table_Registry:
    tables: dict[str, type[Table]]

    def __init__(self) -> None:
        self.tables = {}

    def register_table(self, table_cls: type) -> None:
        self.tables[table_cls.__name__] = table_cls

    def create_table(self, name: str) -> "Optional[Table]":
        if name not in self.tables:
            return None
        return self.tables[name]()

    def __str__(self) -> str:
        return "Table Registry:\n" + "\n".join(
            f"- {name} - {table.__doc__}" for name, table in self.tables.items()
        )


table_registry = Table_Registry()


class Table_Meta(type):
    def __new__(
        mcls, name: str, bases: Tuple[type, ...], namespace: dict[str, Any]
    ) -> type:
        if name == "Table" and not bases:
            return super().__new__(mcls, name, bases, namespace)

        columns: list[Column] = []
        main_columns: list[Main_Column] = []
        for attr_name, value in list(namespace.items()):
            if attr_name.startswith("__"):
                continue
            if not isinstance(value, Column):
                raise TypeError(f"Attribute {attr_name} must be instance of column")
            if isinstance(value, Main_Column):
                main_columns.append(value)
            columns.append(value)
            if value.name == "_not_given":
                value.name = attr_name

        namespace["_columns"] = columns
        namespace["_main_columns"] = main_columns
        cls = super().__new__(mcls, name, bases, namespace)
        table_registry.register_table(cls)
        return cls


class Table(metaclass=Table_Meta):
    _main_columns: list[Main_Column]
    _columns: list[Column]
    rows: list[Row]

    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        if type(self) is Table:
            raise TypeError("Table is abstract")
        self.rows = []

    def parse_value(self, value: str, data_type: type) -> Any:
        if data_type is str:
            return value
        if data_type is int:
            return int(value)
        if data_type is float:
            return float(value)
        return data_type(value)

    def parse_row(self, data: list[str]) -> Row:
        if len(data) != len(self._main_columns):
            raise Parsing_Exception("Number of main columns isn't equal data's length")

        row = Row(self, self._columns)

        for i, value in enumerate(data, start=0):
            column = self._main_columns[i]
            row.__dict__[column.name] = self.parse_value(value, column.data_type)

        for column in self._columns:
            if not isinstance(column, Calc_Column):
                continue
            result = column.calc(row)
            if type(result) is not column.data_type:
                raise TypeError(f"Unknown type of calculation result {column.name}")
            row.__dict__[column.name] = result

        self.rows.append(row)
        return row

    def parse_rows(self, data: list[list[str]]) -> list[Row]:
        return [self.parse_row(row) for row in data]

    def __str__(self) -> str:
        return (
            "-" * 50
            + "\n"
            + self.__class__.__name__.center(50)
            + "\n"
            + "-" * 50
            + "\n"
            + "\n".join(str(row) for row in self.rows)
        )


class Parsing_Exception(Exception):
    pass
