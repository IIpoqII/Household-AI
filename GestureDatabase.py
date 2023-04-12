import mysql.connector
from multipledispatch import dispatch


class GestureDatabase():
    def __init__(self, username="root", password="password", host="127.0.0.1", database="HouseholdAI"):
        conn = mysql.connector.connect(username, password, host, database)
        self.Cursor = conn.cursor()
        self.pCursor = conn.cursor(prepared=True)

    def add_device(self, device_name):
        self.Cursor.execute("select id from Devices")
        row_count = self.Cursor.rowcount
        self.insert_into_table_values("Devices", device_name, row_count+1)

    def insert_gesture_into_database(self, gesture_name):
        self.Cursor.execute("select id from Gestures")
        row_count = self.Cursor.rowcount
        self.insert_into_table_values("Gestures", gesture_name, row_count+1)

    def connect_gesture_to_device_action(self, gesture_name, device_name, action):
        self.Cursor.execute("select id from Gestures where name = %s", gesture_name)
        result_set = self.Cursor.fetchall()
        gid = result_set[0][0]
        self.Cursor.execute("select id from Devices where name = %s", device_name)
        result_set = self.Cursor.fetchall()
        did = result_set[0][0]
        self.insert_into_table_values("DeviceAction", action, did, gid)

    def remove_device(self, device_name):
        self.Cursor.execute("select id from Devices where name = %s", device_name)
        result_set = self.Cursor.fetchall()
        did = result_set[0][0]
        self.delete_from_table_where("DeviceAction", "did = " + did)
        self.delete_from_table_where("Devices", "id = " + did)
        self.update_table_set_columns_where("Devices", "did = did - 1", "did > " + did)

    def remove_gesture_from_database(self, gesture_name):
        self.Cursor.execute("select id from Gestures where name = %s", gesture_name)
        result_set = self.Cursor.fetchall()
        gid = result_set[0][0]
        self.delete_from_table_where("DeviceAction", "gid = " + gid)
        self.delete_from_table_where("Gestures", "id = " + gid)
        self.update_table_set_columns_where("Gestures", "gid = gid - 1", "gid > " + gid)

    def remove_gesture_from_action(self, action, device_name, gesture_name):
        self.Cursor.execute("select id from Gestures where name = %s", gesture_name)
        result_set = self.Cursor.fetchall()
        gid = result_set[0][0]
        self.Cursor.execute("select id from Devices where name = %s", device_name)
        result_set = self.Cursor.fetchall()
        did = result_set[0][0]
        query = "delete from DeviceAction where action = %s and did = %s and gid = %s"
        value_data = (action, did, gid)
        self.Cursor.execute(query, value_data)

    def delete_from_table_where(self, table, where_clause):
        query = "delete from " + table + " where " + where_clause
        self.Cursor.execute(query)

    def update_table_set_columns_where(self, table, set_clause, where_clause):
        query = "update " + table + " set " + set_clause + " where " + where_clause
        self.Cursor.execute(query)

    def select_all_from_table(self, table):
        query = "select * from " + table
        self.Cursor.execute(query)

    @dispatch(any, any)
    def select_columns_from_table(self, column1, table):
        query = "select %s from " + table
        column_data = column1
        self.Cursor.execute(query, column_data)

    @dispatch(any, any, any)
    def select_columns_from_table(self, column1, column2, table):
        query = "select %s, %s from " + table
        column_data = column1, column2
        self.Cursor.execute(query, column_data)

    @dispatch(any, any, any, any)
    def select_columns_from_table(self, column1, column2, column3, table):
        query = "select %s, %s, %s from " + table
        column_data = column1, column2, column3
        self.Cursor.execute(query, column_data)

    @dispatch(any, any)
    def insert_into_table_values(self, table, value1):
        query = "insert into " + table + " values (%s)"
        insert_data = value1
        self.Cursor.execute(query, insert_data)

    @dispatch(any, any, any)
    def insert_into_table_values(self, table, value1, value2):
        query = "insert into " + table + " values (%s, %s)"
        insert_data = (value1, value2)
        self.Cursor.execute(query, insert_data)

    @dispatch(any, any, any, any)
    def insert_into_table_values(self, table, value1, value2, value3):
        query = "insert into " + table + " values (%s, %s, %s)"
        insert_data = (value1, value2, value3)
        self.Cursor.execute(query, insert_data)

    @dispatch(any, any, any, any, any)
    def insert_into_table_values(self, table, value1, value2, value3, value4):
        query = "insert into " + table + " values (%s, %s, %s, %s)"
        insert_data = (value1, value2, value3, value4)
        self.Cursor.execute(query, insert_data)
