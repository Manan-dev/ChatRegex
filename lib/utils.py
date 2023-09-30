"""
Miscellaneous utility functions that don't fit anywhere else.
"""


import random
import re

from lib import store


def remove_stopwords(text: str) -> str:
    """
    Removes stopwords from the input text.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with stopwords removed.
    """
    len_before = len(text)

    for stop_word in store.stop_words:
        text = re.sub(
            r"\b" + stop_word + r"\b",
            "",
            text,
            flags=re.IGNORECASE,
        )

    # For debugging purposes. Can be removed later.
    if len_before != len(text) and len(text) == 0:
        print("Warning: Text is empty after removing stopwords.")
    return text


def remove_punctuation(text: str) -> str:
    """
    Removes punctuation from the input text.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with punctuation removed.
    """
    len_before = len(text)

    text = re.sub(r"[^\w\s]", "", text)

    # For debugging purposes. Can be removed later.
    if len_before != len(text) and len(text) == 0:
        print("Warning: Text is empty after removing punctuation.")
    return text


def remove_extra_spaces(text: str) -> str:
    """
    Removes extra spaces from the input text.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with extra spaces removed.
    """
    len_before = len(text)

    text = re.sub(r"\s+", " ", text).strip()

    # For debugging purposes. Can be removed later.
    if len_before != len(text) and len(text) == 0:
        print("Warning: Text is empty after removing extra spaces.")
    return text


def create_text_variation(text: str) -> str:
    """
    Replaces words in the input text with synonyms from a predefined list of alternatives.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with replaced synonyms.
    """
    for synonym, synonym_list in store.alternatives_map.items():

        def get_replacement(match):
            """
            Returns a random synonym for the matched word in the input string.

            Args:
                match (re.Match): A match object containing the word to be replaced.

            Returns:
                str: A randomly chosen synonym for the matched word, with the same casing as the original word.
            """
            original = match.group(0)

            rnd_synonym = random.choice(synonym_list)

            # print("-" * 40)
            # print("original:", original)
            # print("synonym_list:", synonym_list)
            # print("rnd_synonym:", rnd_synonym)

            # Preserve the original casing
            if original.islower():
                rnd_synonym = rnd_synonym.lower()
            elif original.isupper():
                rnd_synonym = rnd_synonym.upper()
            elif original.istitle():
                rnd_synonym = rnd_synonym.title()

            return rnd_synonym

        text = re.sub(
            r"\b" + synonym + r"\b",
            get_replacement,
            text,
            flags=re.IGNORECASE,
        )
    return text
