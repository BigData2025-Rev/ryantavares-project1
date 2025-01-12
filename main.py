"""The main entry point for the CLI store application."""

from decimal import Decimal
from exceptions import (InvalidInputError, InvalidCredentialsError)
from entities import (User, Game)
from service import Service
import logging

logger: logging.Logger
service = Service()

def main():
    logging.basicConfig(filename="logs/p1.log",
                    level=logging.INFO,
                    format='%(asctime)s :: %(levelname)s :: %(message)s')
    global logger
    logger = logging.getLogger(__name__)
    
    intro = "Welcome to The Game Store"
    while True:
        print("\n".ljust(len(intro), '='))
        print(intro)
        print("".ljust(len(intro), '='))
        try:
            option = input("Who are you?:\n" +
                        "[U]ser\n" +
                        "[A]dmin\n" +
                        "[Q]uit\n" +
                        ">> ").upper()
            if option == 'U':
                user_prescreen()
            elif option == 'A':
                admin_prescreen()
            elif option == 'Q':
                quit()
            else:
                raise InvalidInputError(valid_keys=['u', 'a', 'q'])
        except InvalidInputError as e:
            print(e)

def user_prescreen():
    while True:
        try:
            option = input("What would you like to do?\n" +
                        "[L]og in\n" +
                        "[C]reate an account\n" +
                        "[B]ack\n" +
                        ">> ").upper()
            if option == 'L':
                username = input("Enter a username: \n" +
                                ">> ")
                password = input("Enter a password: \n" +
                                ">> ")
                user = service.login(username, password)
                if user:
                    print("Login successful!")
                    user_mode(user)
            elif option == 'C':
                username = input("Enter a username: \n" +
                                ">> ")
                password = input("Enter a password: \n" +
                                ">> ")
                date_of_birth = input("Enter your date of birth (YYYY-MM-DD): \n" +
                                ">> ")
                if service.create_user(username, password, date_of_birth):
                    print("Account created!")
            elif option == 'B':
                break
            else:
                raise InvalidInputError(valid_keys=['l', 'c', 'b'])
        except InvalidInputError as e:
            print(e)

def user_mode(user:User):
    while True:
        try:
            print("\nWelcome {username}!\n".format(username=user.username))
            option = input("What would you like to do?\n" +
                            "[B]rowse store\n" +
                            "Your [I]nventory\n" +
                            "Your [O]rder History\n" +
                            "Your [W]allet\n" +
                            "[L]og out\n" +
                            ">> ").upper()
            if option == 'B':
                browse_store(user)
            elif option == 'I':
                view_user_inventory(user)
            elif option == 'O':
                user_order_history(user.user_id)
            elif option == 'W':
                manage_wallet(user)
            elif option == 'L':
                print("Logging out...")
                logger.info("User [%s] logged out", user.username)
                del user
                break
            else:
                raise InvalidInputError(['b', 'g', 'i', 'o', 'w', 'l'])
        except InvalidInputError as e:
            print(e)

def user_order_history(user_id):
    recent_orders = service.recent_orders_by_user(user_id)
    start = 0
    end = 5 if len(recent_orders) >= 5 else len(recent_orders)
    while end <= len(recent_orders):
        for i in range(start, end):
            if i < len(recent_orders):
                if i == start:
                    recent_orders[i].show(include_header=True)
                else:
                    recent_orders[i].show()
        else:
            option = input("What would you like to do?\n" +
                    "[Enter] to load more orders\n"
                    "[B]ack\n" +
                    ">> ").upper()
            if option == 'B':
                break
        start = end
        end = end + 5 if end + 5 <= len(recent_orders) else len(recent_orders)

def view_user_inventory(user:User):
    while True:
        try:
            print("\nYour Inventory".center(30, '='))
            print("gID\t" + "Qty\t" + "Title")
            games = service.get_games_in_user_inventory(user)
            unique_games = sorted(set(games), key=lambda game: game.game_id)
            for game in unique_games:
                print(f"{game.game_id}\t" + f"{[game.game_id for game in games].count(game.game_id)}\t" + f"{game.name}")

            #TODO: Implement gifting.
            option = input("\nWhat would you like to do?\n" +
                            "[Game ID] [User Name] to gift a game to another user\n"
                            "[B]ack\n" +
                            ">> ").upper()
            if option == 'B':
                break
            else:
                raise InvalidInputError(['GAME_ID USERNAME', 'b'])
        except InvalidInputError as e:
            print(e)
        

def manage_wallet(user:User):
    """Flow for user to view and add funds to wallet."""
    while True:
        try:
            user.show_wallet()
            option = input("\nWhat would you like to do?\n" +
                        "[A]dd funds to your wallet\n" +
                        "[B]ack\n"
                        ">> ").upper()
            print()
            if option == 'A':
                option = input("How much would you like to add?\n" +
                        ">> $").upper()
                if service.purchase_wallet_funds(user, round(float(option), 2)):
                    print("Thank you for your purchase!")
                    print(f"Added {option} to your wallet\n")
            elif option == 'B':
                break
            else:
                raise InvalidInputError(['a', 'b'])
        except (InvalidInputError, ValueError) as e:
            if type(e) == ValueError: print("Please enter a valid number.")
            else: print(e)

def browse_store(user:User):
    """Browse and select available games in the store."""
    # TODO: Add options to sort results
    games = service.get_all_games()

    # View 5 games at a time.
    start = 0
    end = 5 if len(games) >= 5 else len(games)
    while end <= len(games):
        for i in range(start, end):
            if i < len(games):
                game = games[i]
                game.show_truncated()
        else:
            option = input("[Game Number] to view more details\n"
                "[Enter] to load more games\n"
                "[B]ack\n"
                ">> ").upper()
            print()
            if option in [str(game.game_id) for game in games]:
                view_game(option, user)
                continue
            elif option == 'B':
                break
        start = end
        end = end + 5 if end + 5 <= len(games) else len(games)

def view_game(game_id, user:User):
    """Display detailed information about the given game and provide the option to buy it"""
    game = service.get_game_by_id(game_id)
    if game:
        while True:
            try:
                game.show_detailed()
                user.show_wallet()
                option = input(f"[A]dd {game.name} to cart?\n"
                            "[B]ack\n"
                            ">> ").upper()
                if option == 'A':
                    user.cart.add(game, game.price)
                    if user.will_purchase():
                        if service.purchase_games(user, user.cart.games):
                            print("\nPurchase successful!")
                            service.add_games_to_user(user, user.cart.games)
                            user.cart.empty()
                    else:
                        continue
                elif option == 'B':
                    break
                else:
                    raise InvalidInputError(['a', 'b'])
            except InvalidInputError as e:
                print(e)

def admin_prescreen():
    try:
        password = "password"
        option = input("Please enter the admin password: ")
        if option == password:
            print("Success! Welcome, admin.")
            logger.info("Admin logged in")
            admin_mode()
        else:
            raise InvalidCredentialsError("Incorrect admin password.")
    except (InvalidCredentialsError) as e:
        print(e)

def admin_mode():
    while True:
        try:
            option = input("What would you like to do?\n" +
                        "[V]iew data\n" +
                        "Make changes to [G]ames\n" +
                        "Make changes to [U]sers\n" +
                        "[L]og out\n" +
                        ">> ").upper()
            if option == 'V':
                while True:
                    option = input("What would you like to do?\n" +
                            "View [U]sers\n"
                            "View [O]rders\n"
                            "[B]ack\n" +
                            ">> ").upper()
                    if option == 'U':
                        pass
                    elif option == 'O':
                        admin_view_orders()
                    elif option == 'B':
                        break
                    else:
                        raise InvalidInputError(['u', 'o', 'b'])
            elif option == 'G':
                print("Add, update, or delete games in store")
            elif option == 'U':
                print("Update or delete users")
            elif option == 'L':
                logger.info("Admin logged out")
                break
            else:
                raise InvalidInputError(valid_keys=['v', 'g', 'u', 'l'])
        except InvalidInputError as e:
            print(e)

def admin_view_orders():
    recent_orders = service.get_recent_orders()
    start = 0
    end = 5 if len(recent_orders) >= 5 else len(recent_orders)
    while end <= len(recent_orders):
        for i in range(start, end):
            if i < len(recent_orders):
                if i == start:
                    recent_orders[i].show(include_header=True)
                else:
                    recent_orders[i].show()
        else:
            option = input("What would you like to do?\n" +
                    "[Enter] to load more orders\n"
                    "[B]ack\n" +
                    ">> ").upper()
            if option == 'B':
                break
        start = end
        end = end + 5 if end + 5 <= len(recent_orders) else len(recent_orders)
    


if __name__ == "__main__":
    main()