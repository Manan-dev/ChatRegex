"""
Miscellaneous utility functions that don't fit anywhere else.
"""


import logging
import random
import re
import string
import unicodedata
from pprint import pformat, pprint

from lib import store, utils


def extract_unicode_charset(text: str) -> set[str]:
    """
    Extracts the set of unicode characters from the input text.

    Args:
        text (str): The input text to be processed.

    Returns:
        set[str]: The set of unicode characters in the input text.
    """
    # only unicode characters
    return set(text) - set(string.printable)


def remove_unicode_diacritics(text: str) -> str:
    """
    Removes diacritical marks from any characters in the input text.
    Keeps the underlying base character.

    Args:
        text (str): The input text to be processed.

    Returns:
        str: The input text with diacritical marks removed.
    """
    # Normalize to NFD form, which decomposes composed characters into base characters and diacritical marks
    text = unicodedata.normalize("NFD", text)

    # Filter out characters that are not spacing marks (i.e., diacritical marks)
    for char in extract_unicode_charset(text):
        if unicodedata.category(char) == "Mn":
            text = text.replace(char, "")

    return text


def normalize_character_set(text: str) -> str:
    """
    Translates UTF-8 characters to ASCII characters and equivalent punctuation.
    1. Removes diacritical marks while keeping the underlying base character.
    2. Translates special characters to their ASCII equivalents.

    Args:
        text (str): The input text to be processed.

    Returns:
        str: The input text with UTF-8 characters translated to ASCII characters.
    """
    logging.info("Normalizing character set...")

    logging.debug(f"Unicode charset before: {extract_unicode_charset(text)}")

    text = remove_unicode_diacritics(text)

    # Translation table for special characters
    translation_table = str.maketrans(
        {
            "’": "'",
            "‘": "'",
            "”": '"',
            "“": '"',
            "…": "...",
            "•": "*",
            "–": "-",  # en dash
            "—": "-",  # em dash
            "―": "-",  # horizontal bar
            "æ": "ae",
            "£": "",
            "œ": "",  # ae ligature
        }
    )

    # Translate the text using the table
    text = text.translate(translation_table)

    charset_after = extract_unicode_charset(text)
    if len(charset_after) > 0:
        logging.warning(f"Unicode characters left not translated: {charset_after}.")

    return text


def re_union(*args):
    """
    Creates a regex union of the input arguments.

    Args:
        *args (str): The input strings to be joined.

    Returns:
        str: A regex union of the input strings.
    """
    return "(" + ")|(".join(list(set(args))) + ")"


def remove_stopwords(text: str) -> str:
    """
    Removes stopwords from the input text.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with stopwords removed.
    """
    len_before = len(text)

    text = re.sub(
        r"\b({rgx})\b".format(
            rgx=re_union(*store.stop_words),
        ),
        "",
        text,
        flags=re.IGNORECASE,
    )

    # For debugging purposes. Can be removed later.
    if len_before != len(text) and len(text) == 0:
        logging.warning("Text is empty after removing stopwords.")
    return text


def join_paragraph_lines(text: str) -> str:
    """
    Joins lines that are part of the same paragraph.
    This is to fix random newlines in the middle of sentences caused by how the text was originally extracted.
    Parameters:
      text (string): Text to process.
    Returns:
      processed_text (string): Processed text.
    """
    pattern = r"([^\s])\n([^\s])"
    return re.sub(pattern, r"\1 \2", text)


def add_sentence_delimiter(text: str) -> str:
    """
    Adds a sentence delimiter to split up the sentences

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with a sentence delimiters
    """
    # text = re.sub(r"[.!?]+", " <END_SENTENCE> ", text)
    return re.sub(
        store.RegexPatterns.Processing.SENTENCE_SPLITTING,
        store.SpecialTokens.END_OF_SENTENCE + "\n",
        text,
    )


def add_search_term_tags(text: str, search_terms_map: dict[str, list[str]]) -> str:
    """
    Adds search term tags to the input text.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with search term tags.
    """
    logging.debug("Adding search term tags...")

    for key, terms in search_terms_map.items():
        # TODO: Remove this or only do under debug mode
        # for debugging purposes we can print out the matches

        pattern = r"\b({union})\b".format(
            union=utils.re_union(*list([key] + terms)),
        )

        matches = re.findall(
            pattern,
            text,
            # flags=re.IGNORECASE,
        )
        logging.debug(
            pformat(
                {
                    "key": key,
                    "pattern": pattern,
                    "num_matches": len(matches),
                },
                sort_dicts=False,
            )
        )

        # add tag after any matches
        text = re.sub(
            pattern,
            r"\1 <{tag}>".format(tag=key.upper()),
            text,
            # flags=re.IGNORECASE,
        )

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

    text = re.sub(f"[{string.punctuation}]", "", text)

    # For debugging purposes. Can be removed later.
    if len_before != len(text) and len(text) == 0:
        logging.warning("Text is empty after removing punctuation.")
    return text


def remove_extra_whitespace(
    text: str,
    max_consecutive_spaces: int = 1,
    max_consecutive_newlines: int = 3,
) -> str:
    """
    Removes extra spaces from the input text.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with extra spaces removed.
    """
    len_before = len(text)

    # [^\S\r\n] -> any whitespace EXCEPT newlines and carriage returns

    # max_consecutive_spaces
    text = re.sub(
        r"[^\S\r\n]{" + str(max_consecutive_spaces) + r",}",
        " " * max_consecutive_spaces,
        text,
    )

    # max_consecutive_newlines
    text = re.sub(
        r"[\r\n]{" + str(max_consecutive_newlines) + r",}",
        "\n" * max_consecutive_newlines,
        text,
    )

    # Also strip leading and trailing whitespace on each line
    text = re.sub(r"^[^\S\r\n]+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[^\S\r\n]+$", "", text, flags=re.MULTILINE)

    # For debugging purposes. Can be removed later.
    if len_before != len(text) and len(text) == 0:
        logging.warning("Text is empty after removing extra whitespace.")
    return text.strip()


def create_permutation_map(lists_of_terms: list[list[str]]):
    """
    Given a list of lists containing alternative words/phrases, create a map
    where each word/phrase is mapped to the entire list of alternatives.
    This can be done once and used for constant-time lookups.
    """
    permutation_map = {}
    for alts in lists_of_terms:
        alts = list(set(map(str.strip, alts)))
        for s in alts:
            permutation_map[s.lower()] = alts

    return permutation_map


def create_text_variation(text: str) -> str:
    """
    Replaces words in the input text with synonyms from a predefined list of alternatives.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with replaced synonyms.
    """
    for synonym, synonym_list in store.response_phrase_permutation_map.items():

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
