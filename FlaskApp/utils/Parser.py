from classes.Courier import Courier
from classes.Order import Order
from utils.db import DataBase


class Parser:

    def __init__(self):
        pass

    @staticmethod
    def parse_couriers_to_db(response, data_base: DataBase):
        for i in response.keys():
            for j in response.get(i):
                courier = Courier()
                courier.courier_id = j.get("courier_id")
                courier.courier_type = courier.CourierType[j.get('courier_type')]
                courier.set_working_hours(j.get('working_hours'))
                courier.regions = list(set(j.get('regions')))
                data_base.save_courier(courier)

    @staticmethod
    def parse_orders_to_db(response, data_base: DataBase):
        for i in response.keys():
            for j in response.get(i):
                order = Order()
                order.order_id = j.get("order_id")
                order.weight = j.get('weight')
                order.set_delivery_hours(j.get('delivery_hours'))
                order.region = j.get('region')
                data_base.save_order(order)
