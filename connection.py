"""Sets up a connection to the MySQL database."""

import mysql.connector
import mysql_config as config
import logging

logger = logging.getLogger(__name__)

def connect_to_mysql():
    """Returns a connection to the p1 MySQL database."""
    try:
        cnx = mysql.connector.connect(user=config.user, password=config.password,
                                    host=config.host,
                                    database='p1')

        logger.info("Connected to MySQL database")
        return cnx
    except mysql.connector.Error as e:
        logger.error(f"MySQL Connector Error: {e.msg}")
        return
    except Exception as e:
        logger.error(f"General Error Connecting: {str(e)}")
        return