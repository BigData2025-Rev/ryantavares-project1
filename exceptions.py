"""Module for custom exceptions."""

class UnderAgeError(Exception):
    pass

class ExistenceError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class InvalidInputError(Exception):
    def __init__(self, valid_keys: list[str], message=""):
        self.valid_keys = valid_keys
        self.message=message
        
    def __str__(self):
        bold = "\033[1m"
        red = '\033[91m'
        end = "\033[0m"
        return red + bold + "Invalid input. Try: " + ", ".join(self.valid_keys) + end + "\n"