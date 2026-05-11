from mparser.base import Calc_Column, Filters, Main_Column, Table


class Smeta(Table):
    name = Main_Column(data_type=str)
    cost = Main_Column(data_type=float)
    count = Main_Column(data_type=int)
    price = Calc_Column(data_type=float, calc=lambda row: row.cost * 1.1)
    earn = Calc_Column(
        data_type=float, calc=lambda row: (row.price - row.cost) * row.count
    )

    class Meta(Table.Meta):
        """Подсчет выручки за список товаров"""

        display_name = "Смета"
        filters: Filters = [lambda row: row.cost > 50]
