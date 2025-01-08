"""Service Layer for verifying incoming/outgoing requests to the database."""

from dao import Dao
import datetime as dt
from exceptions import (UnderAgeError, AlreadyExistsError, InvalidCredentialsError)
import logging

logger = logging.getLogger(__name__)

class Service():
    def __init__(self):
        self.dao = Dao()

    def create_user(self, username, password, date_of_birth):
        """If given user data is valid, calls dao to insert user to the database.
        Returns true if user was inserted into the database, false otherwise.
        """
        # TODO: Store secured form of password
        try:
            if not username:
                raise ValueError("Username must not be empty.")
            if len(password) < 6:
                raise ValueError("Password must be at least 6 characters long.")
            if Service.years_since_date(date_of_birth) < 13:
                raise UnderAgeError("Must be 13 years of age or older.")
            if self.dao.select_user_by_username(username):    
                raise AlreadyExistsError("A user with that username already exists.")
        except (ValueError, UnderAgeError, AlreadyExistsError) as e:
            print(e)
            return False
        else:
            return self.dao.insert_user(username, password, date_of_birth)
        
    def login(self, username, password):
        """If given username and password matches a user in the database, return True. If no match, return false."""
        try:
            if self.dao.user_by_username_password(username, password):
                logger.info("User %s logged in", (username))
                return True
            else:
                raise InvalidCredentialsError("Incorrect username/password combination.")
        except InvalidCredentialsError as e:
            print(e)
            return False
        
    def get_all_games(self):
        return self.dao.all_games()
    
    # TODO: Move years_since_date to more appropriate, reusable location.
    def years_since_date(date):
        """Returns the number of years since the given date."""
        try:
            then = dt.datetime.strptime(date, '%Y-%m-%d')
            now = dt.datetime.now()
            years = now.year - then.year
            if now.month < then.month:
                years -= 1
            elif now.month == then.month and now.day < then.day:
                years -= 1
            return years
        except ValueError:
            raise ValueError("Wrong date format. Use (YYYY-MM-DD)")

