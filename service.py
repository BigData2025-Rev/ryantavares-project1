"""Service Layer for verifying incoming/outgoing requests to the database."""

from entities import (User, Game)
from dao import Dao
import datetime as dt
from decimal import (Decimal, InvalidOperation)
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
            if self.dao.user_by_username(username):    
                raise AlreadyExistsError("A user with that username already exists.")
        except (ValueError, UnderAgeError, AlreadyExistsError) as e:
            print(e)
            return False
        else:
            return self.dao.insert_user(username, password, date_of_birth)
        
    def login(self, username, password):
        """If given username and password matches a user in the database, return the User. If no match, return None."""
        try:
            user = self.dao.user_by_username_password(username, password)
            if user:
                logger.info("User [%s] logged in", (username))
                del user['password']
                user = User(**user)
                return user
            else:
                raise InvalidCredentialsError("Incorrect username/password combination.")
        except InvalidCredentialsError as e:
            print(e)
            return None
        
    def get_all_games(self):
        return self.dao.all_games()
    
    def get_game_by_id(self, game_id):
        try:
            game = self.dao.game_by_id(game_id)
            if game:
                return game
            else:
                raise ValueError("Game with that id does not exist")
        except ValueError as e:
            print(e)

    def get_games_in_user_inventory(self, user:User) -> list[Game]:
        """Gets games that a user has purchased."""
        return self.dao.games_in_user_inventory(user.user_id)

    def purchase_games(self, user:User, games: list[Game]):
        """Makes a purchase.
        Returns True if the purchase could be completed, False otherwise.
        """
        try:
            if len(games) == 0:
                raise ValueError("There must be games in the order to make a purchase.")
            for game in games:
                if not self.of_age_for_game(user, game):
                    raise UnderAgeError(f"You are not of age to buy {game.name}.")
            total_cost = Decimal(0.00)
            for game in games:
                total_cost += game.price - (game.price * game.discount_percent)
                if user.wallet < total_cost:
                    raise ValueError("You don't have enough funds!")
                
            if self.dao.insert_order(user.user_id, dt.datetime.now(), total_cost, games):
                new_wallet = user.wallet - total_cost
                if self.update_wallet_funds(user, new_wallet):
                    return True
        except (ValueError, UnderAgeError) as e:
            print(e)
            return False
        
    def purchase_wallet_funds(self, user:User, amount):
        """Purchases wallet funds for a given user."""
        try:
            amount = Decimal(amount)
            if amount <= Decimal(0.00):
                raise ValueError
            else:
                if self.dao.insert_order(user.user_id, dt.datetime.now(), amount):
                    new_amount = user.wallet + amount
                    return self.update_wallet_funds(user, new_amount)
        except (ValueError, InvalidOperation) as e:
            print("Please enter a positive monetary value.")
    
    def update_wallet_funds(self, user:User, amount:Decimal):
        """Update a user's wallet funds."""
        if amount >= Decimal(0.00):
            if self.dao.update_user_wallet(user.user_id, amount):
                user.wallet = amount
                return True
        else:
            print("Cannot have negative wallet funds.")
            return False
    
    def add_games_to_user(self, user:User, games:list[Game]):
        try:
            if len(games) == 0:
                raise ValueError("There must be games to add to user.")
            for game in games:
                if not self.of_age_for_game(user, game):
                    raise UnderAgeError(f"You are not of age to buy {game.name}.")
            else:
                self.dao.insert_user_games(user.user_id, games)
                return True
        except (ValueError, UnderAgeError) as e:
            print(e)
            return False
        
    def of_age_for_game(self, user:User, game:Game):
        age = Service.years_since_date(user.date_of_birth.__str__())
        if self.dao.game_if_of_age(game.game_id, age):
            return True
        else:
            return False
    
    # TODO: Move years_since_date to more appropriate, reusable location.
    def years_since_date(date:str):
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

