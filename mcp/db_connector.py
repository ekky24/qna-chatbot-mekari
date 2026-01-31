import mysql.connector

def connect_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="P@ssw0rd",
        database="qna_chatbot_mekari",
        port=3306
    )
    cursor = conn.cursor()
        
    return conn, cursor

def close_conn(conn):
    conn.close()