import abc
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

type Filter = Callable[[BaseRow], bool]
type Filters = list[Filter]


class ParserRegistry:
    """A registry of all parsers"""

    parsers: "Dict[str, BaseParser]"
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

    def get_parser(self, file_path: Path) -> "Optional[BaseParser]":
        """Get parser by file extension"""
        for parser in self.parsers.values():
            if parser.match(file_path):
                return parser
        return None

    def list_parsers(self) -> "Dict[str, BaseParser]":
        return self.parsers

    def __str__(self) -> str:
        return "Parser Registry:\n" + "\n".join(
            f"- {parser}" for parser in self.parsers.values()
        )


parser_registry = ParserRegistry()


class BaseParser(abc.ABC):
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


class BaseRow:
    """Contains values from one row. \
Values can be obtained by column's name (row.title, row.cost). \
Note that this class is abstract and every table generates it dynamicly"""

    __slots__: list[str] = []

    def __init__(self, columns: list[Column]) -> None:
        pass

    def __str__(self) -> str:
        raise NotImplementedError("This method generates dynamicly")


class Column(abc.ABC):
    """(Abstract) Declares a column in table"""

    name: str
    data_type: type


class MainColumn(Column):
    def __init__(self, *, name: Optional[str] = None, data_type: type) -> None:
        self.name = name or "_not_given"
        self.data_type = data_type


class CalcColumn(Column):
    calc: Callable[[BaseRow], Any]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        data_type: type,
        calc: Callable[[BaseRow], Any],
    ):
        self.name = name or "_not_given"
        self.data_type = data_type
        self.calc = calc


def Calculation(data_type: type, name: Optional[str] = None) -> Any:
    def decorator(func: Callable[[BaseRow], Any]) -> CalcColumn:
        return CalcColumn(name=name, data_type=data_type, calc=func)

    return decorator


class TableRegistry:
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
            f"- {table.Meta.display_name} ({name}) - {table.Meta.description}"
            for name, table in self.tables.items()
        )


table_registry = TableRegistry()


class TableMeta(type):
    def __new__(
        mcls, name: str, bases: Tuple[type, ...], namespace: dict[str, Any]
    ) -> type:
        if name == "Table" and not bases:
            return super().__new__(mcls, name, bases, namespace)

        columns: list[Column] = []
        main_columns: list[MainColumn] = []
        for attr_name, value in list(namespace.items()):
            if attr_name.startswith("__"):
                continue
            if attr_name == "Meta":
                continue
            if not isinstance(value, Column):
                raise TypeError(f"Attribute {attr_name} must be instance of column")
            if isinstance(value, MainColumn):
                main_columns.append(value)
            columns.append(value)
            if value.name == "_not_given":
                value.name = attr_name

        namespace["_columns"] = columns
        namespace["_main_columns"] = main_columns

        if "Meta" not in namespace:

            class Meta:
                description = ""
                display_name = name
                filters = []

            namespace["Meta"] = Meta
        meta = namespace["Meta"]
        meta.description = meta.__doc__ or namespace["__doc__"] or ""
        meta.filters = meta.__dict__.get("filters", [])
        meta.display_name = meta.__dict__.get("display_name", name)

        cls = super().__new__(mcls, name, bases, namespace)

        table_registry.register_table(cls)
        return cls


class Table(metaclass=TableMeta):
    _main_columns: list[MainColumn]
    _columns: list[Column]
    rows: list[BaseRow]

    class Meta:
        display_name: str
        description: str
        filters: list[Filter]

    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        if type(self) is Table:
            raise TypeError("Table is abstract")
        self.rows = []

    def generate_dynamic_row_class(self) -> type:
        def __init__(self: BaseRow, columns: list[Column]) -> None:
            for column in columns:
                setattr(self, column.name, None)

        def __str__(self: BaseRow) -> str:
            return "; ".join(
                [
                    str(getattr(self, name))
                    for name in self.__slots__
                    if not name.startswith("__")
                ]
            )

        return type(
            f"{self.__class__.__name__}Row",
            (BaseRow,),
            {
                "__slots__": tuple(column.name for column in self._columns),
                "__init__": __init__,
                "__str__": __str__,
            },
        )

    def parse_value(self, value: str, data_type: type) -> Any:
        if data_type is str:
            return value
        if data_type is int:
            return int(value)
        if data_type is float:
            return float(value)
        return data_type(value)

    def parse_row(self, data: list[str]) -> BaseRow:
        if len(data) != len(self._main_columns):
            raise ParsingException("Number of main columns isn't equal data's length")

        row_type = self.generate_dynamic_row_class()
        row = row_type(self._columns)

        for i, value in enumerate(data, start=0):
            column = self._main_columns[i]
            setattr(row, column.name, self.parse_value(value, column.data_type))

        for column in self._columns:
            if not isinstance(column, CalcColumn):
                continue
            result = column.calc(row)
            if type(result) is not column.data_type:
                raise TypeError(f"Unknown type of calculation result {column.name}")
            setattr(row, column.name, result)

        match_filters = True
        for filter in self.Meta.filters:
            match_filters = match_filters and filter(row)

        if match_filters:
            self.rows.append(row)

        return row

    def parse_rows(self, data: list[list[str]]) -> list[BaseRow]:
        return [self.parse_row(row) for row in data]

    def __str__(self) -> str:
        return (
            "-" * 50
            + "\n"
            + f"{self.Meta.display_name.center(50)}\n"
            + f"{self.Meta.description}\n"
            + "-" * 50
            + "\n"
            + "; ".join([column.name for column in self._columns])
            + "\n"
            + "\n".join(str(row) for row in self.rows)
        )


class ParsingException(Exception):
    pass
