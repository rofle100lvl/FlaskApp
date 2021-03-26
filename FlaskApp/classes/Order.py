import re
import datetime


class Order:
    def __init__(self, order_tuple: tuple = None):
        self.order_id = -1
        self.courier_id = -1
        self.region = []
        self.delivery_hours = []
        self.weight = -1
        self.assign_time = ''
        self.complete_time = ''
        if order_tuple:
            self.order_id = order_tuple[0]
            self.weight = order_tuple[1]
            self.region = order_tuple[2]
            self.set_delivery_hours(order_tuple[3].split(';'))
            self.courier_id = order_tuple[4]
            self.status = order_tuple[5]
            self.assign_time = order_tuple[6]
            self.complete_time = order_tuple[7]

    def order_time_to_db(self):
        s = ""
        for delivery_hour in self.delivery_hours:
            s += delivery_hour[0] + '-' + delivery_hour[1]
            s += ';'
        return s[0:-1]

    def set_delivery_hours(self, times: list):
        for time in times:
            if not re.fullmatch('\d\d:\d\d-\d\d:\d\d', time):
                return
            start_delivery_time = time[0:5]
            end_delivery_time = time[6:11]
            self.delivery_hours.append((start_delivery_time, end_delivery_time))
