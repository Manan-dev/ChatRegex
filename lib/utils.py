"""
Miscellaneous utility functions that don't fit anywhere else.
"""


import os
import random
import re
import string

from lib import store


def re_union(*args):
    """
    Creates a regex union of the input arguments.

    Args:
        *args (str): The input strings to be joined.

    Returns:
        str: A regex union of the input strings.
    """
    return "|".join(args)


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
    text = re.sub(r"[.!?]+", " <END_SENTENCE> ", text)

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
        print("Warning: Text is empty after removing punctuation.")
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
        print("Warning: Text is empty after removing extra spaces.")
    return text.strip()


def process_toc_elements(text: str) -> str:
    """
    Process the TOC elements in the text to determine if the chapter headings need updating.
    Args:
        text (str): Text to be parsed and checked.

    Returns:
        text (str): Text with proper chapter headings.
    """
    print("Detecting if text contains a table of contents....")
    
    table_of_contents = re.search(store.RegexPatterns.Processing.TOC, text, re.MULTILINE)
    
    if table_of_contents:
        table_of_contents = re.sub(r'^Contents\n', "", table_of_contents.group()).strip().split('\n')
        
        chapter_list = []
        for element in table_of_contents:
            chapter_list.append(element.strip())
        
        has_chapter_format = re.search(r"((chapter) (?:\d{1,3}|" + store.RegexPatterns.Processing.ROMAN_NUMERALS + r")(?: .*)?)$", text, flags=re.MULTILINE | re.IGNORECASE)

        if has_chapter_format == None:
            print("Updating chapter heading format...")
            text = update_chapter_headings(text, chapter_list)
        else:
            print("Correct chapter heading format. Returning...")
    
    else:
        print("No table of contents found in the text.")
        
    return text


def update_chapter_headings(text: str, chapter_list) -> str:
    """
    Will update the chapter headings of the text to "Chapter .....".
    Args:
        text (str): Text to be updated.
        chapter_list (_type_): List of chapter headings in the text.

    Returns:
        text (str): Return the text with modified chapter headings.
    """
    for elem in chapter_list:
        matches = re.findall(f"^{elem}$", text)

        if len(matches) > 2:
            print(f"WARN: Expected 2 matches but got {len(matches)}")
            continue
        
        replacement = f'Chapter {elem}'
        text = re.sub(elem, replacement, text)
    
    return text


def create_text_variation(text: str) -> str:
    """
    Replaces words in the input text with synonyms from a predefined list of alternatives.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with replaced synonyms.
    """
    for synonym, synonym_list in store.response_phrase_alts_map.items():

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
