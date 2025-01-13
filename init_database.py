"""This module is meant to initialize the MySQL database with some baked-in game data.
Useful for initializing the database for the first time, or for resetting the database to its initial state.
"""

import mysql.connector
import mysql.connector.cursor 
import mysql_config as config
import datetime as dt
import json
import logging

logger = None
if __name__ != "__main__":
    logger = logging.getLogger(__name__)

def main():
    init_database(abort_if_exists=False)

def init_database(abort_if_exists=True):
    """Initializes/Resets database with baked in game data.
    Set abort_if_exists to True stop the database from being reset if it already exists.
    """
    # Connect to the MySQL database.
    try:
        cnx = mysql.connector.connect(user=config.user, 
                                    password=config.password,
                                    host=config.host)

        logger.info("Connected to MySQL database")
    except mysql.connector.Error as e:
        logger.error(f"MySQL Connector Error: {e.msg}")
        return
    except Exception as e:
        logger.error(f"General Error Connecting: {str(e)}")
        return

    cursor = cnx.cursor()

    if abort_if_exists:
        cursor.execute("SHOW DATABASES LIKE 'p1';")
        if cursor.fetchall():
            return
    
    logger.warning("Resetting database")

    # Initialize database.
    cursor.execute("CREATE DATABASE IF NOT EXISTS p1;")
    cursor.execute("USE p1;")
    drop_tables(cursor)
    create_tables(cursor)
    insert_data(cursor)

    # Close cursor and database connection.
    cursor.close()

    cnx.commit()
    logger.info("Committed changes")

    cnx.close()
    logger.info("Closed connection")

def drop_tables(cursor):
    """Drop all tables in the database."""
    cursor.execute("DROP TABLE IF EXISTS User_Game;")
    cursor.execute("DROP TABLE IF EXISTS Game_Category;")
    cursor.execute("DROP TABLE IF EXISTS Game_Genre;")
    cursor.execute("DROP TABLE IF EXISTS OrderDetails;")
    cursor.execute("DROP TABLE IF EXISTS Orders;")
    cursor.execute("DROP TABLE IF EXISTS Users;")
    cursor.execute("DROP TABLE IF EXISTS Games;")
    cursor.execute("DROP TABLE IF EXISTS Genres;")
    cursor.execute("DROP TABLE IF EXISTS Categories;")
    cursor.execute("DROP TABLE IF EXISTS Ratings;")

def create_tables(cursor):
    """Build the structure of the database."""

    #First, create parent tables.
    cursor.execute(
        """
        CREATE TABLE Users(
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(256) NOT NULL,
            date_of_birth DATE NOT NULL,
            wallet DECIMAL(7,2) DEFAULT 0.00
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE Orders(
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            user_fk INT,
            order_date DATETIME NOT NULL,
            total_cost DECIMAL(7,2),
            FOREIGN KEY (user_fk) REFERENCES Users(user_id) ON DELETE SET NULL
        );
        """
    )
    
    cursor.execute(
    """
    CREATE TABLE Ratings(
        rating CHAR(3) PRIMARY KEY,
        required_age INT NOT NULL
    );
    """
    )

    cursor.execute(
        """
        CREATE TABLE Games(
            game_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(256) NOT NULL,
            price DECIMAL(6,2) NOT NULL,
            rating CHAR(3) DEFAULT 'rp',
            description VARCHAR(512) NOT NULL,
            developer VARCHAR(100) NOT NULL,
            publisher VARCHAR(100) NOT NULL,
            recommendations INT DEFAULT 0,
            release_date DATE NOT NULL,
            metacritic INT DEFAULT NULL,
            discount_percent DECIMAL(5,2) DEFAULT 0.00,
            FOREIGN KEY (rating) REFERENCES Ratings(rating) ON DELETE SET NULL
        );
        """
    )
    
    cursor.execute(
        """
        CREATE TABLE Genres(
            genre VARCHAR(50) PRIMARY KEY
        );
        """
    )
    
    cursor.execute(
        """
        CREATE TABLE Categories(
            category VARCHAR(50) PRIMARY KEY
        );
        """
    )

    # Then, create child tables.
    cursor.execute(
        """
        CREATE TABLE OrderDetails(
            order_fk INT,
            game_fk INT,
            quantity INT CHECK (quantity > 0),
            PRIMARY KEY (order_fk, game_fk),
            FOREIGN KEY (order_fk) REFERENCES Orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (game_fk) REFERENCES Games(game_id)
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE User_Game(
            user_fk INT,
            game_fk INT,
            bound BOOLEAN NOT NULL DEFAULT false,
            playtime_hours FLOAT DEFAULT 0.00,
            quantity_in_inventory INT DEFAULT 0,
            PRIMARY KEY (user_fk, game_fk),
            FOREIGN KEY (user_fk) REFERENCES Users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (game_fk) REFERENCES Games(game_id)
        );
        """
    )    

    cursor.execute(
        """
        CREATE TABLE Game_Genre(
            game_fk INT,
            genre VARCHAR(50),
            PRIMARY KEY (game_fk, genre),
            FOREIGN KEY (game_fk) REFERENCES Games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (genre) REFERENCES Genres(genre) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE Game_Category(
            game_fk INT,
            category VARCHAR(50),
            PRIMARY KEY (game_fk, category),
            FOREIGN KEY (game_fk) REFERENCES Games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (category) REFERENCES Categories(category) ON DELETE CASCADE
        );
        """
    )

def insert_data(cursor):
    # Load baked-in data that will be inserted into the database.
    with open('init_data.json') as infile:
        data = json.load(infile)

    # First, insert data into parent tables.
    insert_query = """INSERT INTO Ratings (rating, required_age) 
                VALUES ('e', 0), ('e10', 10), ('t', 13), ('m', 17), ('ao', 18), ('rp', 0);"""
    cursor.execute(insert_query)

    unique_genres = list({genre for game in data for genre in game['genres']})
    insert_query = "INSERT INTO Genres (genre) VALUES "
    for genre in unique_genres:
        if unique_genres.index(genre) == len(unique_genres) - 1:
            insert_query += "(%s);"
        else:
            insert_query += "(%s), "
    cursor.execute(insert_query, unique_genres)

    unique_categories = list({category for game in data for category in game['categories']})
    insert_query = "INSERT INTO Categories (category) VALUES "
    for category in unique_categories:
        if unique_categories.index(category) == len(unique_categories) - 1:
            insert_query += "(%s);"
        else:
            insert_query += "(%s), "
    cursor.execute(insert_query, unique_categories)

    insert_query = ("INSERT INTO Games "
                "(name, price, rating, description, developer, publisher, recommendations, release_date, metacritic) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);")
    for game in data:
        release_date = dt.datetime.strptime(game['release_date'], '%b %d, %Y')
        insert_data = {
            'name': game['name'],
            'price': game['price'],
            'rating': game['rating'],
            'description': game['description'],
            'developer': game['developer'],
            'publisher': game['publisher'],
            'recommendations': game['recommendations'],
            'release_date': str(release_date.date()),
            'metacritic': game['metacritic']
        }
        cursor.execute(insert_query, list(insert_data.values()))
    
    # Then, insert data into child tables.
    insert_query = "INSERT INTO Game_Genre (game_fk, genre) VALUES (%s, %s);"
    game_id = 1
    for game in data:
        for genre in game['genres']:
            cursor.execute(insert_query, (game_id, genre))
        game_id += 1

    insert_query = "INSERT INTO Game_Category (game_fk, category) VALUES (%s, %s);"
    game_id = 1
    for game in data:
        for category in game['categories']:
            cursor.execute(insert_query, (game_id, category))
        game_id += 1
    

if __name__ == "__main__":
    logging.basicConfig(filename="logs/p1.log",
                level=logging.INFO,
                format='%(asctime)s :: %(levelname)s :: %(message)s')
    logger = logging.getLogger(__name__)
    main()