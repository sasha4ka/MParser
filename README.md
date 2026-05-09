# MParser

A versatile command-line tool for parsing various file formats, built with Python.

## Features

- **JSON Parsing**: Parse JSON files with support for nested objects, arrays, strings, numbers, booleans, and null values.
- **Extensible Architecture**: Easily add support for new file formats by implementing custom parsers.
- **Command-Line Interface**: Simple CLI for parsing files from the terminal.

## Installation

### Prerequisites

- Python 3.14 or higher
- Poetry (for dependency management)

### Install from Source

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd MParser
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

## Usage

Run the parser using Poetry:

```bash
poetry run mparser -f <file-path>
```

### Examples

Parse a JSON file:
```bash
poetry run mparser -f test_file.json
```

### Supported File Formats

- **JSON** (`.json`): Full JSON parsing support
- **XML** (`.xml`): Basic XML parsing (placeholder implementation)

## Development

### Setup Development Environment

1. Install development dependencies:
   ```bash
   poetry install --with dev
   ```

2. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Code Quality

This project uses:
- **Ruff**: For linting and code formatting
- **MyPy**: For static type checking
- **Pre-commit**: For automated code quality checks

### Adding New Parsers

To add support for a new file format:

1. Create a new parser class inheriting from `Base_Parser` in `src/mparser/parsers.py`
2. Implement the `process(self, file_path: Path) -> Any` method
3. Implement the `match(self, file_path: Path) -> bool` method to identify file types
4. The parser will be automatically registered

Example:
```python
class NewFormat_Parser(Base_Parser):
    def process(self, file_path: Path) -> Dict[str, Any]:
        # Your parsing logic here
        pass

    def match(self, file_path: Path) -> bool:
        return file_path.suffix == ".newformat"
```

## Project Structure

```
MParser/
├── src/mparser/
│   ├── __init__.py
│   ├── base.py          # Base parser classes and registry
│   ├── engine.py        # Parsing engine (if applicable)
│   ├── main.py          # CLI entry point
│   └── parsers.py       # Concrete parser implementations
├── tests/
│   └── __init__.py
├── pyproject.toml       # Project configuration
├── poetry.lock          # Dependency lock file
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Aleksandr Basov - sasha4ka99991@gmail.com</content>
<parameter name="filePath">/home/sasha/Projects/week-1/MParser/README.md