import sqlite3
from classes.Courier import Courier
from classes.Order import Order
from datetime import datetime


class DataBase:
    DATABASE = 'mydatabase.db'

    def __init__(self):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS Couriers(
                        courier_id BIGINT NOT NULL PRIMARY KEY, 
                        courier_type TEXT NOT NULL, 
                        regions TEXT NOT NULL ,
                        work_time TEXT NOT NULL
                        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS Orders(
                                order_id BIGINT NOT NULL PRIMARY KEY UNIQUE, 
                                weight REAL NOT NULL, 
                                region BIGINT NOT NULL ,
                                delivery_hours TEXT NOT NULL,
                                courier_id BIGINT DEFAULT NULL,
                                status INTEGER DEFAULT 0,
                                assign_time TEXT DEFAULT NULL,
                                complete_time TEXT DEFAULT NULL
                                )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS Regions_stat(
                                        region BIGINT NOT NULL PRIMARY KEY UNIQUE,
                                        average_time FlOAT,
                                        count BIGINT
                                        )""")

    def save_courier(self, courier: Courier):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"""INSERT INTO Couriers (courier_id, courier_type, regions, work_time) VALUES 
        ({courier.courier_id}, '{courier.courier_type.name}', '{courier.regions_to_db()}', '{courier.work_time_to_db()}')
        """)
        conn.commit()
        cursor.close()

    def update_courier(self, courier: Courier):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"""UPDATE Couriers SET courier_type = '{courier.courier_type.name}', 
        regions = '{courier.regions_to_db()}', work_time= '{courier.work_time_to_db()}'
         WHERE courier_id = {courier.courier_id}
                """)
        conn.commit()
        cursor.close()

    def save_order(self, order: Order):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"""INSERT INTO Orders (order_id, weight, region, delivery_hours) VALUES 
                ({order.order_id}, '{order.weight}', '{order.region}', '{order.order_time_to_db()}')
                """)
        conn.commit()
        cursor.close()

    def get_courier_by_id(self, courier_id):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Couriers WHERE courier_id={courier_id}")
        conn.commit()
        ans = cursor.fetchone()
        cursor.close()
        conn.close()
        return ans

    def get_order_by_id(self, order_id):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Orders WHERE order_id={order_id}")
        conn.commit()
        ans = cursor.fetchone()
        cursor.close()
        conn.close()
        return ans

    def get_orders_to_assign(self, max_weight: float):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Orders WHERE weight<{max_weight}  AND status = 0 ")
        conn.commit()
        ans = cursor.fetchall()
        cursor.close()
        conn.close()
        return ans

    def add_assign_to_order(self, courier_id: int, order_id: int):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE Orders SET courier_id ='{courier_id}', status=1 WHERE order_id = '{order_id}'")
        conn.commit()
        cursor.close()
        conn.close()

    def remove_order_from_courier(self, courier_id, order_id):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE Orders SET courier_id =NULL, status=0, assign_time=NULL  WHERE order_id = '{order_id}'")
        conn.commit()
        cursor.close()
        conn.close()

    def add_assign_time_to_orders(self, order_id, assign_time):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE Orders SET assign_time ='{assign_time}' WHERE order_id = '{order_id}'")
        conn.commit()
        cursor.close()
        conn.close()

    def get_courier_orders(self, courier_id):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Orders WHERE courier_id = {courier_id}")
        conn.commit()
        ans = cursor.fetchall()
        cursor.close()
        conn.close()
        return ans

    def set_complete_time_to_order(self, order, complete_time):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE Orders SET complete_time ='{complete_time}', status = 2 WHERE order_id = {order.order_id}")
        conn.commit()
        cursor.close()
        conn.close()

    def complete_order(self, order, complete_time):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            f"""SELECT * FROM Orders WHERE region = {order.region} AND order_id != {order.order_id} 
                    AND status=2 ORDER BY complete_time ASC""")
        order_tuples = cursor.fetchone()
        last_complete_order = Order(order_tuples)
        actual_complete_time = datetime.strptime(complete_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        assign_time = datetime.strptime(order.assign_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        if last_complete_order.order_id == -1:
            new_average_time = (actual_complete_time - assign_time).total_seconds()
            if new_average_time <= 0:
                return False
            cursor.execute(
                f"INSERT INTO regions_stat (region, count, average_time) VALUES ({order.region}, 0, 0)"
            )
            cursor.execute(
                f"""
                                UPDATE regions_stat 
                                SET average_time = ((average_time * count) 
                                + {new_average_time})/(count+1), count = count +1 
                                where region= {order.region}
                                """
            )
            conn.commit()
            cursor.close()
            conn.close()
            self.set_complete_time_to_order(order, complete_time)
            return True

        last_complete_time = datetime.strptime(last_complete_order.complete_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        new_average_time = (actual_complete_time - last_complete_time).total_seconds()
        if new_average_time <= 0:
            cursor.close()
            conn.close()
            return False
        cursor.execute(
            f"""
                                        UPDATE regions_stat SET average_time = 
                                        ((average_time * count) + {new_average_time})/(count+1), 
                                        count = count +1 WHERE region= {order.region}
                            """
        )
        conn.commit()
        cursor.close()
        conn.close()
        self.set_complete_time_to_order(order, complete_time)
        return True

    def get_average_time(self):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT average_time FROM regions_stat")
        ans = cursor.fetchall()
        cursor.close()
        conn.close()
        return ans

    def get_count_complete_orders(self, courier_id):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Orders WHERE status=2 AND courier_id={courier_id}")
        ans = len(cursor.fetchall())
        cursor.close()
        conn.close()
        return ans

    def clear_tables(self):
        conn = sqlite3.connect(self.DATABASE)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM Couriers")
        cursor.execute(f"DELETE FROM Orders")
        cursor.execute(f"DELETE FROM regions_stat")
        conn.commit()
        cursor.close()
        conn.close()
