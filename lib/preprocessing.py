import logging
import re
import unicodedata

from lib import stop_words, utils


def remove_punctuation(text: str) -> str:
    """
    Removes punctuation from the input text.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with punctuation removed.
    """
    len_before = len(text)

    # text = re.sub(
    #     r"[^\w\s]",
    #     "",
    #     text,
    # )
    text = re.sub(
        r"[^[a-zA-Z0-9\s]+",
        " ",
        text,
    )

    # For debugging purposes. Can be removed later.
    # if len_before != len(text) and len(text) == 0:
    #     logging.warning("Text is empty after removing punctuation.")
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
    # if len_before != len(text) and len(text) == 0:
    #     logging.warning("Text is empty after removing extra whitespace.")
    return text.strip()


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
    for char in utils.extract_unicode_charset(text):
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
    logging.debug(f"Unicode charset before: {utils.extract_unicode_charset(text)}")

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

    charset_after = utils.extract_unicode_charset(text)
    if len(charset_after) > 0:
        logging.warning(f"Unicode characters left not translated: {charset_after}.")

    return text


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
        # r"(( \b({rgx})\b)|(\b({rgx})\b ))".format(
        #     rgx=utils.re_union(*stop_words.stop_words),
        # ),
        r"((\b({rgx})\b))".format(
            rgx=utils.re_union(*stop_words.stop_words),
        ),
        "",
        text,
        flags=re.IGNORECASE,
    )

    # For debugging purposes. Can be removed later.
    if len_before != len(text) and len(text) == 0:
        logging.warning("Text is empty after removing stopwords.")
    return text
