"""The main entry point for the CLI store application."""

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
        print("".ljust(len(intro), '='))
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

def user_mode(user):
    while True:
        try:
            option = input("What would you like to do?\n" +
                            "[B]rowse store\n" +
                            "Your [G]ames\n" +
                            "Your [I]nventory\n" +
                            "Your [O]rder History\n" +
                            "Your [W]allet\n" +
                            "[L]og out\n" +
                            ">> ").upper()
            if option == 'B':
                browse_store(user)
            elif option == 'G':
                print("View your games")
            elif option == 'I':
                print("View your inventory")
            elif option == 'O':
                print("View your Order History")
            elif option == 'W':
                print("View and/or add money to your Wallet")
            elif option == 'L':
                print("Logging out...")
                logger.info("User (%s) logged out", user.username)
                break
            else:
                raise InvalidInputError(['b', 'g', 'i', 'o', 'w', 'l'])
        except InvalidInputError as e:
            print(e)

def browse_store(user):
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
        end += 5

def view_game(game_id, user: User):
    """Display detailed information about the given game and provide the option to buy it"""
    game = Game(**service.get_game_by_id(game_id))
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
                    user.cart.show()
                    user.show_wallet()
                    input("\nEnter any key to continue.\n")
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
                print("View orders and/or users")
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
    


if __name__ == "__main__":
    main()