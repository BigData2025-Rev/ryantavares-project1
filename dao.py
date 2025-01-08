"""Data Access Layer for communicating directly with the MySQL database."""

import mysql.connector.errors
from connection import connect_to_mysql
import logging

logger = logging.getLogger(__name__)

class Dao():
    def __init__(self):
        self.cnx = connect_to_mysql()

    def __del__(self):
        self.cnx.close()
        logger.info("DB connection closed")
    
    def insert_user(self, username, password, date_of_birth):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor() as cursor:
                try:
                    insert_query = "INSERT INTO Users (username, password, date_of_birth) VALUES (%s, %s, %s)"
                    cursor.execute(insert_query, (username, password, date_of_birth))
                    self.cnx.commit()
                    logger.info("Inserted user %s into db", username)
                    return True
                except mysql.connector.Error as e:
                    logger.warning("Failed to insert user %s :: %s", (username, e.msg))
        return False
    
    def select_user_by_username(self, username):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor() as cursor:
                try:
                    cursor.execute("SELECT * FROM Users WHERE username=%s", [username])
                    return cursor.fetchone()
                except mysql.connector.Error as e:
                    logger.warning("Query to select user by username (%s) failed :: %s", (username, e.msg))
    
    def user_by_username_password(self, username, password):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor() as cursor:
                try:
                    cursor.execute("SELECT * FROM Users WHERE username=%s AND password=%s", [username, password])
                    return cursor.fetchone()
                except mysql.connector.Error as e:
                    logger.warning("Query to select user by username (%s) and password (hidden) failed :: %s", (username, e.msg))