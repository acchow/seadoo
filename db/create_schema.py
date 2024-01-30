import mysql.connector
from mysql.connector import Error, MySQLConnection
from config import db

def connect(): 
    conn = None
    try: 
        conn = mysql.connector.connect(
            host=db['host'], 
            database=db['schema'],
            user=db['user'],
            password=db['pw'], 
            port=db['port']
        )
        print('Succesfully connected to database')
    except Error as e: 
        print('Error connecting to database', db['schema'], e)
    return conn


def create_tables(conn: MySQLConnection): 
    cursor = conn.cursor()
    f = open('db/create.sql', 'r')
    queries = f.read().split(';')
    for q in queries: 
        try: 
            cursor.execute(q)
        except Error as e: 
            print('Error creating table', e)

def insert_values(conn: MySQLConnection): 
    cursor = conn.cursor()
    f = open('db/insert.sql', 'r')
    queries = f.read().split(';')
    for q in queries: 
        try: 
            print('inserting\n')
            cursor.execute(q)
            conn.commit()
        except Error as e: 
            print('Error inserting values', e)

if __name__ == "__main__": 
    conn = connect()
    if type(conn) == MySQLConnection: 
        create_tables(conn)
        insert_values(conn)
    conn.close()