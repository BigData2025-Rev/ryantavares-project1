"""The main entry point for the CLI store application."""

import logging

def main():
    logging.basicConfig(filename="logs/p1.log",
                    level=logging.INFO,
                    format='%(asctime)s :: %(levelname)s :: %(message)s')

    while True:
        option = input("Who are you?:\n" +
                    "[U]ser\n" +
                    "[A]dmin\n" +
                    "[Q]uit\n" +
                    ">> ").upper()
        if option == 'U':
            while True:
                option = input("What would you like to do?\n" +
                               "[L]og in\n" +
                               "[C]reate an account\n" +
                               "[Q]uit\n" +
                               ">> ").upper()
                if option == 'L':
                    print("do log in")
                elif option == 'C':
                    print("do create an account")
                elif option == 'Q':
                    break
        elif option == 'A':
            password = "password"
            option = input("Please enter the admin password: ")
            if option == password:
                while True:
                    print("Success")
                    option = input("What would you like to do?\n" +
                                   "[S]tuff\n" +
                                   "[Q]uit\n" +
                                   ">> ").upper()
                    if option == 'S':
                        print("doing stuff")
                    elif option == 'Q':
                        break
        elif option == 'Q':
            quit()


if __name__ == "__main__":
    main()