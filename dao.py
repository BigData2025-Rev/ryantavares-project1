"""Data Access Layer for communicating directly with the MySQL database."""

from entities import (User, Game, Order)
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
                    logger.info("Inserted user [%s] into db", username)
                    return True
                except mysql.connector.Error as e:
                    logger.error("Failed to insert user [%s] :: %s", username, e.msg)
        return False
    
    def user_by_id(self, user_id):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("SELECT * FROM Users WHERE user_id=%s", [user_id])
                    return User(**cursor.fetchone())
                except mysql.connector.Error as e:
                    logger.error("Query to select user by user_id [%s] failed :: %s", user_id, e.msg)
    
    def user_by_username(self, username):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("SELECT * FROM Users WHERE username=%s", [username])
                    return cursor.fetchone()
                except mysql.connector.Error as e:
                    logger.error("Query to select user by username [%s] failed :: %s", username, e.msg)
    
    def user_by_username_password(self, username, password):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("SELECT * FROM Users WHERE username=%s AND password=%s;", [username, password])
                    return cursor.fetchone()
                except mysql.connector.Error as e:
                    logger.error("Query to select user by username [%s] and password failed :: %s", username, e.msg)
    
    def all_games(self):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("SELECT * FROM Games;")
                    games = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT gam.game_id, gen.genre
                        FROM Games gam INNER JOIN Game_Genre gen ON gam.game_id = gen.game_fk;
                        """
                    )
                    genres = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT gam.game_id, cat.category
                        FROM Games gam INNER JOIN Game_Category cat ON gam.game_id = cat.game_fk;
                        """
                    )
                    categories = cursor.fetchall()

                    for game in games:
                        game['genres'] = [genre['genre'] for genre in genres if genre['game_id'] == game['game_id']]
                        game['categories'] = [category['category'] for category in categories if category['game_id'] == game['game_id']]

                    return [Game(**game) for game in games]
                except mysql.connector.Error as e:
                    logger.error("Query to select all games failed :: %s", (e.msg))

    def game_by_id(self, game_id):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("SELECT * FROM Games WHERE game_id=%s;", [game_id])
                    game = cursor.fetchone()
                    game['genres'] = [genre[0] for genre in self.game_genres(game['game_id'])]
                    game['categories'] = [category[0] for category in self.game_categories(game['game_id'])]
                    return Game(**game)
                except mysql.connector.Error as e:
                    logger.error("Query to select game by game_id [%s] failed :: %s", game_id, e.msg)

    def game_genres(self, game_id):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                        SELECT gen.genre
                        FROM Games gam INNER JOIN Game_Genre gen ON gam.game_id = gen.game_fk
                        WHERE gen.game_fk = %s;
                        """
                    , [game_id])
                    return cursor.fetchall()
                except mysql.connector.Error as e:
                    logger.error("Query to select game genres :: %s", (e.msg))

    def game_categories(self, game_id):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                        SELECT cat.category
                        FROM Games gam INNER JOIN Game_Category cat ON gam.game_id = cat.game_fk
                        WHERE cat.game_fk = %s;
                        """
                    , [game_id])
                    return cursor.fetchall()
                except mysql.connector.Error as e:
                    logger.error("Query to select game categories :: %s", (e.msg))
                
    def game_if_of_age(self, game_id, age):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute(
                        """
                        SELECT g.*
                        FROM Games g INNER JOIN Ratings r ON g.rating = r.rating
                        WHERE g.game_id = %s AND r.required_age <= %s;
                        """
                    , [game_id, age])
                    return cursor.fetchone()
                except mysql.connector.Error as e:
                    logger.error("Query to select game by game_id [%s] for user with age [%s] failed :: %s", game_id, age, e.msg)

    def insert_order(self, user_id, order_date, total_cost, games=None):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor() as cursor:
                try:
                    # Insert order into Orders table.
                    insert_query = "INSERT INTO Orders (user_fk, order_date, total_cost) VALUES (%s, %s, %s);"
                    cursor.execute(insert_query, (user_id, order_date, total_cost))

                    # Insert order details into OrderDetails table if this purchse is for games.
                    if games:
                        insert_query = "INSERT INTO OrderDetails (order_fk, game_fk, quantity) VALUES (%s, %s, %s);"
                        order_fk = cursor._last_insert_id
                        for game_fk in set([game.game_id for game in games]):
                            quantity = [game.game_id for game in games].count(game_fk)
                            cursor.execute(insert_query, (order_fk, game_fk, quantity))

                    self.cnx.commit()
                    logger.info("Inserted order_id [%s] by user_id [%s] with total_cost [$%.2f] into db", cursor._last_insert_id, user_id, total_cost)
                    return True
                except mysql.connector.Error as e:
                    logger.error("Failed to insert order by user_id [%s] :: %s", user_id, e.msg)
        return False
    
    def games_in_user_inventory(self, user_id):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                        SELECT g.*, quantity_in_inventory
                        FROM Games g INNER JOIN User_Game ug ON g.game_id = ug.game_fk
                        WHERE user_fk = %s
                        ORDER BY g.name DESC;
                        """
                    , [user_id])
                    rows = cursor.fetchall()
                    games = []
                    for row in rows:
                        for i in range(row[-1]):
                            games.append(Game(*row[0:-1]))
                    return games

                except mysql.connector.Error as e:
                    logger.error("Query to select user_id [%s] games in inventory failed :: %s", user_id, e.msg)
    
    def select_user_game(self, user_id, game_id):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("SELECT * FROM User_Game WHERE user_fk=%s AND game_fk=%s;", [user_id, game_id])
                    return cursor.fetchone()
                except mysql.connector.Error as e:
                    logger.error("Query to select user_id [%s] game by game_id [%s] :: %s", user_id, game_id, e.msg)
    
    def insert_user_games(self, user_id, games):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor() as cursor:
                try:
                    insert_query = "INSERT INTO User_Game (user_fk, game_fk, quantity_in_inventory) VALUES (%s, %s, %s);"
                    game_ids = [game.game_id for game in games]
                    for game_fk in set(game_ids):
                        quantity = game_ids.count(game_fk)
                        in_inventory = self.select_user_game(user_id, game_fk)
                        if in_inventory:
                            self.update_user_game(user_id, game_fk, in_inventory['quantity_in_inventory'] + quantity)
                        else:
                            cursor.execute(insert_query, (user_id, game_fk, quantity))

                    self.cnx.commit()
                    logger.info("Inserted games into user_id [%s] inventory :: %s", user_id, [game.name for game in games])
                    return True
                except mysql.connector.Error as e:
                    logger.error("Failed to insert games into user_id [%s] inventory :: %s", user_id, e.msg)
        return False
    
    def update_user_game(self, user_id, game_id, quantity):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor() as cursor:
                try:
                    update_query = "UPDATE User_Game SET quantity_in_inventory=%s WHERE user_fk=%s AND game_fk=%s;"
                    cursor.execute(update_query, (quantity, user_id, game_id))

                    self.cnx.commit()
                    logger.info("Updated user_id [%s] inventory", user_id)
                    return True
                except mysql.connector.Error as e:
                    logger.error("Failed to update user_id [%s] inventory :: %s", user_id, e.msg)
        return False
    
    def update_user_wallet(self, user_id, amount):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor() as cursor:
                try:
                    update_query = "UPDATE Users SET wallet=%s WHERE user_id=%s;"
                    cursor.execute(update_query, (amount, user_id))

                    self.cnx.commit()
                    logger.info("Updated user_id [%s] wallet balance to %.2f", user_id, amount)
                    return True
                except mysql.connector.Error as e:
                    logger.error("Failed to update user_id [%s] wallet balance :: %s", user_id, e.msg)
        return False
    
    def recent_orders_by_user(self, user_id):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("SELECT * FROM Orders WHERE user_fk=%s ORDER BY order_date DESC;", [user_id])
                    orders = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT g.name, od.quantity, od.order_fk
                        FROM Games g INNER JOIN OrderDetails od ON g.game_id = od.game_fk;
                        """
                    )
                    details = cursor.fetchall()
                    for order in orders:
                        order['quantities_by_game'] = [{detail['name']:detail['quantity']} for detail in details if detail['order_fk'] == order['order_id']]
                    return [Order(**order) for order in orders]
                except mysql.connector.Error as e:
                    logger.error("Query to select orders by user_id [%s] failed :: %s", user_id, e.msg)

    def recent_orders(self):
        if self.cnx and self.cnx.is_connected():
            with self.cnx.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("SELECT * FROM Orders ORDER BY order_date DESC;")
                    orders = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT g.name, od.quantity, od.order_fk
                        FROM Games g INNER JOIN OrderDetails od ON g.game_id = od.game_fk;
                        """
                    )
                    details = cursor.fetchall()
                    for order in orders:
                        order['quantities_by_game'] = [{detail['name']:detail['quantity']} for detail in details if detail['order_fk'] == order['order_id']]
                    return [Order(**order) for order in orders]
                except mysql.connector.Error as e:
                    logger.error("Query to select all recent orders failed :: %s", e.msg)