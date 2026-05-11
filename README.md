# MParser
Проект парсера, который поддерживает различные форматы файлов и таблиц. 
Функционал может быть расширен при помощи добавляемых модулей (см.ниже)

### Подготовка окружения
```sh
poetry install
```

### Использование
```
usage: MParser [-h] [-r] [-f FILE] [-t TABLE] [-s]

Module parser for different filetypes and data schemes

options:
  -h, --help         show this help message and exit
  -r, --registry     show table and parser registry
  -f, --file FILE    select file for parsing
  -t, --table TABLE  select table for parsing
  -s, --short        dont show table rows
```

### Примеры
```sh
poetry run mparser  # файлы и таблица будут выбраны интерактивно
poetry run mparser -f "files.json" -t Smeta
poetry run mparser -t Smeta  # если будет найден файл files.json приоритет будет у него
```

### Пример files.json
```json
[
   "samples/sample1.csv",
   "samples/sapmle2.json"
]
```

# Расширение функционала
Функционал может быть расширен при помощи:
1. Изменения файла tables.py для добавления таблиц
2. Изменения файла parsers.py для добавления типов данных

### Таблицы
Таблицы создаются декларативно при помощи реализации абстрактного класса (`base.Table`). 
При создании класса он автоматически регистрируется в реестре и доступен при выборе.

```python3
from mparser.base import Table, Main_Column, Calc_Column, Calculation


class Smeta(Table):
   """Подсчитывает выручку с продажи товаров"""
   name = Main_Column(data_type=str)
   cost = Main_Column(data_type=float)
   count = Main_Column(data_type=int)
   price = Calc_Column(data_type=float, calc=lambda row: row.cost * 1.1)

   @Calculation(data_type=float)
   def earn(row: Row) -> float:
      return row.count * (row.price - row.cost)
```

*Основные столбцы* (`Main_Column`) - значения, получаемые из файлов  
*Расчетные столбцы* (`Calc_Column`) - значения, расчитываемые из других столбцов  

Объект класса (`Row`) представляет из себя одну строку из таблицы

Декоратор (`@Calculation`) может быть использован для более простого способа создания расчетных столбцов

Документация класса будет переданна в реестр при регестрации таблицы
```
poetry run mparser -r
Mparser v0.1.0
(...)
Table Registry:
- Smeta - Подсчитывает выручку с продажи товаров
```

### Парсеры
Парсеры реализуют абстрактный класс (`base.Base_Parser`). При создании парсера он автоматически регистрируется в реестре и доступен для выбора. Пример парсера:
```python3
from mparser.base import Base_Parser


class My_Parser(Base_Parser):
   def process(self, file_path: Path) -> list[list[str]]:
      """Логика обработки файла"""
      return result

   def match(self, file_path: Path) -> bool:
      return file_path.suffix == ".my_file_extension"
```

`Base_Parser.process` реализует логику обработки файла. Возвращает список строк, каждая строка - `list[str]`  
`Base_Parser.match` отвечает за проверку совпадения типа файла

# Contribution
1. Сделайте форк репозитория
2. Внесите необходимые изменения в новой ветке
3. Создайте pull request
