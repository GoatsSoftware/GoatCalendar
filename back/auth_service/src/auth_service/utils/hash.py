from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_str_chain(str_chain: str) -> str:
    """
    Converts a plain-text string into a secure cryptographic hash.

    This function is used during user registration or password updates.
    It applies the Argon2 algorithm to create a one-way representation
    of the input string that is resistant to brute-force attacks.

    :param str_chain: The raw string or password to be protected.
    :return: A salted and hashed version of the input string.
    """
    return pwd_context.hash(str_chain)


def compare_text_with_hash(plain_text: str, text_hashed: str) -> bool:
    """
    Validates a raw string against a previously generated hash.

    This function safely compares user input during login against the
    stored hash. It is designed to handle potential errors in hash
    formatting gracefully by returning a failure status instead of
    crashing the application.

    :param plain_text: The unhashed string provided by the user.
    :param text_hashed: The secure hash retrieved from the database.
    :return: A boolean indicating whether the text matches the hash.
    """
    try:
        return pwd_context.verify(plain_text, text_hashed)
    except ValueError:
        return False
