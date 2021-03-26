from enum import Enum
import re
from datetime import time

from classes.Order import Order


class Courier:
    class CourierType(Enum):
        foot = 10
        bike = 15
        car = 50

    courier_id = -1
    regions = []
    work_times = []
    courier_type = None

    def __init__(self, courier_tuple: tuple = None):
        self.courier_id = -1
        self.regions = []
        self.work_times = []
        if courier_tuple:
            print(courier_tuple)
            self.courier_id = courier_tuple[0]
            self.courier_type = self.CourierType[courier_tuple[1]]
            self.regions = [int(item) for item in courier_tuple[2].split(';')]
            self.set_working_hours(courier_tuple[3].split(';'))

    def to_string(self):
        print("ID: ", self.courier_id)
        print("TYPE: ", self.courier_type)
        print("REGIONS: ", self.regions)
        print("WORK TIMES: ", self.work_times)

    def regions_to_db(self):
        return ';'.join(map(str, self.regions))

    def work_time_to_db(self):
        time_to_db = ''
        for work_time in self.work_times:
            time_to_db += work_time[0] + '-' + work_time[1] + ';'
        return time_to_db[0:-1]

    def set_working_hours(self, times: list):
        for work_time in times:
            if not re.fullmatch('\d\d:\d\d-\d\d:\d\d', work_time):
                return
            start_work_time = work_time[0:5]
            end_work_time = work_time[6:11]
            self.work_times.append((start_work_time, end_work_time))

    def update_courier(self, response, data_base):
        if 'courier_type' in response:
            self.courier_type = self.CourierType[response.get('courier_type')]
        if 'working_hours' in response:
            self.set_working_hours(response.get("working_hours"))
        if 'regions' in response:
            self.regions = response.get("regions")
        order_tuples = data_base.get_courier_orders(self.courier_id)

        for order_tuple in order_tuples:
            order = Order(order_tuple=order_tuple)
            if order.status == 2:
                continue
            if not (order.region in self.regions):
                data_base.remove_order_from_courier(self.courier_id, order.order_id)
                continue
            if not self.time_crossing(self.work_times, order.delivery_hours):
                data_base.remove_order_from_courier(self.courier_id, order.order_id)
                continue
            if not self.courier_type.value >= order.weight:
                data_base.remove_order_from_courier(self.courier_id, order.order_id)
                continue

    @staticmethod
    def time_crossing(working_times: list, delivery_times: list):
        for working_time in working_times:
            start_work, end_work = working_time
            for delivery_time in delivery_times:
                start_delivery, end_delivery = delivery_time
                if max(start_work, start_delivery) <= min(end_delivery, end_work):
                    return True
                else:
                    continue
        return False

    def assign_orders(self, order_tuples: list, data_base):
        complete_orders = {"orders": []}
        for order_tuple in order_tuples:
            order = Order(order_tuple=order_tuple)
            if not (order.region in self.regions):
                continue
            if self.time_crossing(self.work_times, order.delivery_hours):
                complete_orders.get("orders").append({"id": order.order_id})
                data_base.add_assign_to_order(self.courier_id, order.order_id)
        return complete_orders

    def to_dict(self):
        return {
            "courier_id": self.courier_id,
            "courier_type": self.courier_type.name,
            "regions": self.regions,
            "working_hours": self.work_time_to_db()
        }
