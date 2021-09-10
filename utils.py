import sqlite3
import logging
logging.basicConfig(level=logging.DEBUG)

sqlite_db = "krypto.db"

queries = {
    'CREATE': """CREATE TABLE IF NOT EXISTS USERINFO (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USER TEXT,
                ALERT_PRICE REAL,
                EMAIL TEXT,
                STATUS TEXT DEFAULT "CREATED")
                """,
    'INSERT': """INSERT INTO USERINFO (USER, ALERT_PRICE, EMAIL) 
                VALUES ('{user}', {alert_price}, '{email}')
                """,
    'DELETE': """UPDATE USERINFO SET STATUS = 'DELETED' WHERE
                USER = '{user}' and ALERT_PRICE = {alert_price}
                """,
    'FETCH': """SELECT USER, ALERT_PRICE, EMAIL, STATUS from USERINFO WHERE
                USER LIKE '%{user}%'
                """,
    'ALERT': """SELECT * from USERINFO where ALERT_PRICE > {btc_price} AND STATUS='CREATED'
                """,
    'UPDATE': """UPDATE USERINFO SET STATUS='{status}' WHERE ID={id} and USER='{user}' and 
                ALERT_PRICE={alert_price}
                """
}


def execute_select(query):
    try:
        con = sqlite3.connect(sqlite_db)
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        cursor.execute(query)
        op = cursor.fetchall()
        cursor.close()
        con.close()
        return op

    except Exception as e:
        logging.error(f"Error while Creating Table: {e}")
        return None


def execute_alter(query):
    try:
        con = sqlite3.connect(sqlite_db)
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        cursor.close()
        con.close()
    except Exception as e:
        logging.error(f"Error while Altering Table: {e}")


def create_table():
    execute_alter(queries['CREATE'])



