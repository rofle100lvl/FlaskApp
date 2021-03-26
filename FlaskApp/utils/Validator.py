import re


def validate_time(research):
    for work_time in research:
        if not (type(work_time) == str):
            return False
        if not (re.fullmatch('\d\d:\d\d-\d\d:\d\d', work_time)):
            return False
        if not(0 <= int(work_time[:2]) < 24 and 0 <= int(work_time[3:5]) < 60 and 0 <= int(
                work_time[6:8]) < 24 and 0 <= int(work_time[9:]) < 60):
            return False
        if not (int(work_time[:2]) - int(work_time[6:8]) < 0 or (int(work_time[:2]) - int(
                work_time[6:8]) == 0 and int(work_time[3:5]) - int(work_time[9:]) <= 0)):
            return False
    return True


def is_regions_int(research: list):
    for k in research:
        if not type(k) == int:
            return False
    return True


class Validator:
    @staticmethod
    def validate_set_couriers(response, database):
        error_couriers = {"couriers": []}
        complete_couriers = {"couriers": []}
        for i in response.keys():
            for j in response.get(i):
                if 'courier_type' in j and 'courier_id' in j and 'working_hours' in j and 'regions' in j and len(
                        j) == 4:
                    if type(j.get('courier_id')) == int and j.get('courier_id') > 0 and \
                            database.get_courier_by_id(courier_id=j.get('courier_id')) is None:
                        if j.get('courier_type') == 'foot' or j.get('courier_type') == 'bike' or j.get(
                                'courier_type') == 'car':
                            if len(j.get('regions')) > 0 and is_regions_int(j.get('regions')):
                                if len(j.get('working_hours')) > 0 and validate_time(j.get('working_hours')):
                                    complete_couriers["couriers"].append({'id': j.get('courier_id')})
                                    continue
                error_couriers["couriers"].append({'id': j.get('courier_id')})
        return [error_couriers, complete_couriers]

    @staticmethod
    def validate_set_orders(response: dict, database):
        error_orders = {"orders": []}
        complete_orders = {"orders": []}

        for i in response.keys():
            for j in response.get(i):
                if 'order_id' in j and 'weight' in j and 'region' in j and 'delivery_hours' in j and len(j) == 4:

                    if type(j.get('order_id')) == int and j.get('order_id') > 0 and \
                            database.get_order_by_id(order_id=j.get('order_id')) is None:

                        if (type(j.get('weight')) == float or type(j.get('weight')) == int) and j.get('weight') > 0:

                            if type(j.get('region')) == int and j.get('region') > 0:

                                if len(j.get('delivery_hours')) > 0 and validate_time(j.get('delivery_hours')):
                                    complete_orders["orders"].append({'id': j.get('order_id')})

                                    continue
                error_orders["orders"].append({'id': j.get('order_id')})
        return [error_orders, complete_orders]

    @staticmethod
    def validate_update_courier(data):
        if 'courier_type' in data or 'working_hours' in data or 'regions' in data and len(data) < 4:
            if not ('courier_type' in data) or (data.get('courier_type') == 'foot' or
                                                data.get('courier_type') == 'bike' or data.get(
                        'courier_type') == 'car'):
                if not ('regions' in data) or (len(data.get('regions')) > 0 and is_regions_int(data.get('regions'))):
                    if not ('working_hours' in data) or (
                            len(data.get('working_hours')) > 0 and validate_time(data.get('working_hours'))):
                        return True
        return False

    @staticmethod
    def validate_assign(data, database):
        if 'courier_id' in data and len(data) == 1 and type(data.get('courier_id')) == int:
            if database.get_courier_by_id(courier_id=data.get('courier_id')):
                return True
        return False

    @staticmethod
    def validate_complete(data, database):
        if 'courier_id' in data and 'order_id' in data and 'complete_time' in data and len(data) == 3:
            if type(data.get('courier_id')) == int and data.get("courier_id") > 0 and \
                    database.get_courier_by_id(courier_id=data.get('courier_id')):
                if type(data.get('order_id')) == int and data.get("order_id") > 0 and \
                        database.get_order_by_id(order_id=data.get('order_id')):
                    if re.match('\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{1,}Z', data.get("complete_time")):
                        return True
        return False
