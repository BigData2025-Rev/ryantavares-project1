"""This module contains various entities that are used throughout the program."""

from decimal import Decimal
from exceptions import (InvalidInputError)

class Game():
    def __init__(self, game_id, name, price, rating, description, developer, publisher, recommendations, release_date, metacritic, discount_percent, genres=[], categories=[]):
        self.game_id = game_id
        self.name = name
        self.price = Decimal(price)
        self.rating = rating
        self.description =  description
        self.developer = developer
        self.publisher = publisher
        self.recommendations = recommendations
        self.release_date = release_date
        self.metacritic = metacritic
        self.discount_percent = discount_percent
        self.genres = genres
        self.categories = categories

    def __eq__(self, other):
        return self.game_id == other.game_id
    
    def __hash__(self):
        return hash((self.game_id, self.name))
    
    def show_truncated(self):
        format = ("[{game_id}]\t{name}\n"
                "\tDev: {developer} | Pub: {publisher} | Released: {release_date} | Rated: {rating} | Metacritic: {metacritic}\n"
                "\tGenres: {genres} | Categories: {categories}\n"
                "\t${price}\n")
        print(format.format(game_id=self.game_id, name=self.name, developer=self.developer,
                        publisher=self.publisher, release_date=self.release_date, rating=self.rating.upper(),
                        genres=", ".join(self.genres), categories=", ".join(self.categories), price=self.price,
                        metacritic=f"{self.metacritic}/100" if self.metacritic else 'NA'))

    def show_detailed(self):
        format = ("\tTitle:\t\t{name}\n"
                "\tDescription:\t{description}\n"
                "\tDeveloper:\t{developer}\n"
                "\tPublisher:\t{publisher}\n"
                "\tRelease Date:\t{release_date}\n"
                "\tRated:\t\t{rating}\n"
                "\tGenres:\t\t{genres}\n"
                "\tCategories:\t{categories}\n"
                "\tMetacritic:\t{metacritic}\n"
                "\tPrice:\t\t${price}\n"
                "\tDiscount:\t{discount_percent}\n")
        desc = self.description
        desc1 = desc[0:len(desc) // 2]
        desc2 = desc[len(desc) // 2:]
        print()
        print(format.format(name=self.name, description="\n\t\t\t".join([desc1,desc2]), developer=self.developer,
                            publisher=self.publisher, release_date=self.release_date, rating=self.rating.upper(),
                            genres=", ".join(self.genres), categories=", ".join(self.categories), price=self.price,
                            metacritic=f"{self.metacritic}/100" if self.metacritic else 'NA',
                            discount_percent=f"{self.discount_percent*100}%"))

class Cart():
    """Defines a Cart which holds multiple products and carries a total of their prices."""
    def __init__(self, games: list[Game]=None, total=Decimal(0.00)):
        self.games = [] if games == None else games
        self.total= total

    def __del__(self):
        self.empty()

    def add(self, game, price):
        self.games.append(game)
        self.total += Decimal(price)

    def remove(self, game, price):
        self.games.remove(game)
        self.total -= Decimal(price)

    def empty(self):
        self.total = Decimal(0.00)
        self.games = []

    def show(self):
        print("\nYour cart:")
        for game in self.games:
            print(f"${game.price}\t{game.name}")
        print("".center(15, "-"))
        print(f"${self.total}\tTotal")

class User():
    """Defines a User. Password, not included."""
    def __init__(self, user_id, username="", date_of_birth="", wallet=0.00):
        self.user_id=user_id
        self.username = username
        self.date_of_birth=date_of_birth
        self.wallet = wallet
        self.cart = Cart()

    def show_wallet(self):
        print("${wallet:.2f}\tIn your wallet".format(wallet=self.wallet))

    def will_purchase(self):
        while True:
            self.cart.show()
            self.show_wallet()
            try:
                option = input("\n[M]ake purchase?\n"
                                "[B]ack\n"
                                ">> ").upper()
                if option == 'M':
                    return True
                elif option == 'B':
                    return False
                else:
                    InvalidInputError('m', 'b')
            except InvalidInputError as e:
                print(e)