import json
from flask import Flask, request, abort, make_response
from datetime import datetime
from classes.Courier import Courier
from utils.Validator import Validator
from utils.Parser import Parser
from utils.db import DataBase
from classes.Order import Order
from app import app, data_base

courier_manager = Parser()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.errorhandler(400)
def not_found(error):
    return make_response("Bad request", 404)


def get_min_average_time(average_times):
    min_time = average_times[0][0]
    for average_time in average_times:
        min_time = min(min_time, average_time[0])
    return min_time


@app.route('/couriers/<int:courier_id>', methods=['GET'])
def get_courier(courier_id: int):
    courier = Courier(data_base.get_courier_by_id(courier_id))
    if courier.courier_id == -1:
        abort(400)
    courier_info = courier.to_dict()
    average_times = data_base.get_average_time()
    if not average_times:
        abort(400)
    t = get_min_average_time(average_times)
    courier_info["rating"] = (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5
    if courier.courier_type.name == "foot":
        courier_info["earnings"] = 500 * 2 * data_base.get_count_orders(courier.courier_id)
    elif courier.courier_type.name == "bike":
        courier_info["earnings"] = 500 * 5 * data_base.get_count_orders(courier.courier_id)
    elif courier.courier_type.name == "car":
        courier_info["earnings"] = 500 * 9 * data_base.get_count_orders(courier.courier_id)
    return json.dumps(courier_info)


@app.route('/couriers/<int:courier_id>', methods=['PATCH'])
def update_courier(courier_id: int):
    response = request.get_json(force=True)
    if not request.is_json:
        abort(400)

    courier = Courier(data_base.get_courier_by_id(courier_id))
    if courier.courier_id == -1:
        abort(400)

    if Validator.validate_update_courier(response):
        courier.update_courier(response, data_base)
        data_base.update_courier(courier)
        return json.dumps(courier.to_dict())
    abort(400)


@app.route('/orders', methods=['POST'])
def create_orders():
    response = request.get_json(force=True)
    if not request.is_json:
        abort(400)
    cour = Validator.validate_set_orders(response, data_base)
    error_orders = cour[0]
    complete_orders = cour[1]
    if len(error_orders.get("orders")) == 0:
        courier_manager.parse_orders_to_db(response, data_base)
        return json.dumps(complete_orders), 201
    return json.dumps({"validation_error": error_orders}), 400


@app.route('/orders/assign', methods=['POST'])
def create_assign():
    response = request.get_json(force=True)
    if not request.is_json:
        abort(400)
    if not Validator.validate_assign(response, data_base):
        abort(400)
    courier_id = response.get('courier_id')
    courier = Courier(data_base.get_courier_by_id(courier_id))
    orders = data_base.get_orders_to_assign(courier.courier_type.value)
    complete_orders = courier.assign_orders(orders, data_base)
    if len(complete_orders.get("orders")) == 0:
        return json.dumps(complete_orders), 200
    else:
        complete_orders["assign_time"] = datetime.utcnow().isoformat() + 'Z'
        for order_id in complete_orders.get('orders'):
            data_base.add_assign_time_to_orders(order_id.get("id"), complete_orders.get("assign_time"))
        return json.dumps(complete_orders), 200


@app.route('/orders/complete', methods=['POST'])
def complete_order():
    response = request.get_json(force=True)
    if not request.is_json:
        abort(400)
    if not Validator.validate_complete(response, data_base):
        abort(400)
    courier = Courier(data_base.get_courier_by_id(response.get('courier_id')))
    order = Order(data_base.get_order_by_id(response.get('order_id')))
    if courier.courier_id == -1 or order.order_id == -1 or order.courier_id != courier.courier_id:
        abort(400)
    if not data_base.complete_order(order, response.get("complete_time")):
        abort(400)
    return json.dumps({"order_id": order.order_id})


@app.route('/couriers', methods=['POST'])
def create_couriers():
    response = request.get_json(force=True)
    if not request.is_json:
        abort(400)
    cour = Validator.validate_set_couriers(response, data_base)
    error_couriers = cour[0]
    complete_couriers = cour[1]

    if len(error_couriers.get("couriers")) == 0:
        courier_manager.parse_couriers_to_db(response, data_base)
        return json.dumps(complete_couriers), 201
    return json.dumps({"validation_error": error_couriers}), 400
