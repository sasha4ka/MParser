from mparser.base import Calc_Column, Main_Column, Table


class Smeta(Table):
    """Подсчет выручки за список товаров"""

    name = Main_Column(data_type=str)
    cost = Main_Column(data_type=float)
    count = Main_Column(data_type=int)
    price = Calc_Column(data_type=float, calc=lambda row: row.cost * 1.1)
    earn = Calc_Column(data_type=float, calc=lambda row: row.price * row.count)
