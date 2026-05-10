from mparser.base import Calc_Column, Main_Column, Table


class Smeta(Table):
    """Подсчет выручки за список товаров"""

    name = Main_Column(name="name", data_type=str)
    cost = Main_Column(name="cost", data_type=float)
    count = Main_Column(name="count", data_type=int)
    price = Calc_Column(name="price", data_type=float, calc=lambda row: row.cost * 1.1)
    earn = Calc_Column(
        name="earn", data_type=float, calc=lambda row: row.price * row.count
    )
