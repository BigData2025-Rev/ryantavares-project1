"""The main entry point for the CLI store application."""

from exceptions import (InvalidInputError, InvalidCredentialsError)
from service import Service
import logging

service = Service()
logger: logging.Logger

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
                if service.login(username, password):
                    print("Login successful!")
                    user_mode(username)
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

def user_mode(username):
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
                print("Browse store")
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
                logger.info("User (%s) logged out", username)
                break
            else:
                raise InvalidInputError(['b', 'g', 'i', 'o', 'w', 'l'])
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