from mparser.base import CalcColumn, Filters, MainColumn, Table


class Smeta(Table):
    name = MainColumn(data_type=str)
    cost = MainColumn(data_type=float)
    count = MainColumn(data_type=int)
    price = CalcColumn(data_type=float, calc=lambda row: row.cost * 1.1)
    earn = CalcColumn(
        data_type=float, calc=lambda row: (row.price - row.cost) * row.count
    )

    class Meta(Table.Meta):
        """Подсчет выручки за список товаров"""

        display_name = "Смета"
        filters: Filters = [lambda row: row.cost > 50]
