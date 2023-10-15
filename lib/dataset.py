"""
Functions for loading and processing text dataset.    
"""
import logging
import re
from enum import Enum
from pprint import pformat

from lib import preprocessing, search_terms, utils

from .special_tokens import SpecialTokens


class RegexPatterns(str, Enum):
    DELIM_PROJ_GUTENBERG = (
        r"^\s*\*\*\* (?:START|END) OF THE PROJECT GUTENBERG EBOOK [\w ]+ \*\*\*$"
    )

    # Source: https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch06s09.html
    ROMAN_NUMERALS = (
        r"(?=[MDCLXVI])"
        r"M*(?:C[MD]|D?C*)"
        r"(?:X[CL]|L?X*)"
        r"(?:I[XV]|V?I*)"  # noqa: E501
    )
    CHAPTER_TITLE = (
        r"(?:chapter|part) (?:\d{1,3}|"
        + ROMAN_NUMERALS
        + r")(?:\.? .*?)?"  # noqa: E501
    )

    TABLE_OF_CONTENTS = r"(^Contents\n+(?:.*\n)+?$\n\n)"

    SENTENCE_SPLITTING = (
        r"(?<!\w\.\w.)"
        # Don't match abbreviations like ["U. S.", "U. K."]
        r"(?<![A-Z]\.)"
        # Don't match 2-letter abbreviations like ["Mr.", "Ms.", "Dr."]
        r"(?<!(Mr|Ms|Dr|Sr|Jr|St|Lt|Co|Mt)\.)"
        # Don't match 3-letter abbreviations like ["Mrs.", "Rev.", "Col."]
        r"(?<!(Mrs|Rev|Col|Maj|Gen|Sgt)\.)"
        r"(?<!(\,\"))"
        r"(((?<=(\.|\!|\?|:))\s)|"
        r"((?<=(\.[\"\']|\![\"\']))\s)|"
        r"((?<=(\"|\'))\n))"  # noqa: E501
    )
    # Note: previous versions, keeping them commented out for reference
    # SENTENCE_SPLITTING = r"(?<=[.!?])\s+"
    # SENTENCE_SPLITTING = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"
    # SENTENCE_SPLITTING = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|:|\"|\!)\s"

    def __str__(self) -> str:
        return self.value


def read_data(file_path):
    """
    Reads the text file and returns a list of lines.
    Parameters:
      file_path (string): Path to the file to read.
    Returns:
      text (string): Text read from the file.
    """
    logging.info(f"Reading data from file: {file_path}")
    # with open(file_path, "r", encoding="ascii", errors="ignore") as f:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    return "".join(map(str, lines))


def extract_body(text: str):
    """
    Filters out text between 'START OF THE PROJECT' and 'END OF THE PROJECT'.
    Parameters:
      text (string): Text to filter.
    Returns:
      filtered_text (string): Filtered text.
    """
    # Examples:
    # *** START OF THE PROJECT GUTENBERG EBOOK THE MAN IN THE BROWN SUIT ***
    # *** END OF THE PROJECT GUTENBERG EBOOK THE MAN IN THE BROWN SUIT ***
    logging.info("Extracting body of text...")

    split_text = re.split(RegexPatterns.DELIM_PROJ_GUTENBERG, text, flags=re.MULTILINE)

    if len(split_text) != 3:
        logging.warning(
            f"Expected 3 splits for body of text. Found {len(split_text)} splits."
        )
        return text

    _, body_text, _ = split_text

    return body_text.strip()


def matches_chapter_title(text: str) -> bool:
    """
    Checks if the text matches a chapter title.
    Args:
        text (str): Text to be parsed and checked.

    Returns:
        bool: True if the text matches a chapter title, False otherwise.
    """
    match = re.match(
        RegexPatterns.CHAPTER_TITLE,
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    return match is not None


def get_toc(text: str) -> tuple[str | None, list[str]]:
    """
    Extracts the table of contents from the text.
    Args:
        text (str): Text to be parsed and checked.

    Returns:
        list[str]: List of chapter headings.
    """
    logging.debug("Searching for table of contents...")

    toc = re.search(
        RegexPatterns.TABLE_OF_CONTENTS,
        text,
        flags=re.MULTILINE,
    )
    if not toc:
        logging.debug(" - No table of contents found.")
        return None, []

    toc_text = toc.group()

    toc_elems: list[str] = (
        re.sub(
            r"^Contents\n+",
            "",
            toc_text,
        )
        .strip()
        .split("\n")
    )
    logging.debug(f" - Found {len(toc_elems)} table of contents elements.")

    return toc_text, toc_elems


def normalize_chapter_headings(text: str, chapter_headings: list[str]) -> str:
    """
    Process the TOC elements in the text to determine if the chapter headings need updating.
    Args:
        text (str): Text to be parsed and checked.

    Returns:
        text (str): Text with proper chapter headings.
    """
    logging.info("Normalizing chapter headings...")
    logging.debug(f"Chapter headings: {pformat(chapter_headings)}")

    for elem in chapter_headings:
        elem = elem.strip()
        # If this chapter title already matches we don't need to update it to match
        if matches_chapter_title(elem):
            logging.debug(
                f'Chapter heading "{elem}" already matches the expected pattern. Skipping replacement.'
            )
            continue

        text_occurances = re.findall(
            f"^{elem}$",
            text,
            flags=re.MULTILINE,
        )
        if len(text_occurances) not in (1, 2):
            logging.warning(
                f'Expected 1 or 2 matches for chapter heading: "{elem}". Found {len(text_occurances)} matches.'
            )

        replacement = f"Chapter {elem}"
        if not matches_chapter_title(replacement):
            logging.warning(
                f'Chapter heading replacement "{replacement}" does not match the expected pattern. Skipping replacement.'
            )
            continue

        logging.debug(f'Replacing "{elem}" with "{replacement}"...')

        text = re.sub(elem, replacement, text)

    return text


def add_chapter_delimiter(text: str) -> str:
    """
    Adds a chapter delimiter to split up the chapters.
    Args:
        text (str): Text to be parsed and checked.

    Returns:
        text (str): Text with chapter delimiters.
    """

    # if we have a table of contents we can use it to help us add chapter delimiters
    toc_text, toc_elems = get_toc(text)
    if toc_text and toc_elems:
        logging.debug("Removing table of contents from text...")
        # remove the toc from the text
        text = re.sub(
            RegexPatterns.TABLE_OF_CONTENTS,
            "",
            text,
            flags=re.MULTILINE,
        )
        text = normalize_chapter_headings(text, toc_elems)

    pattern = r"^{rgx}$".format(
        rgx=utils.re_union(
            "PROLOGUE",
            RegexPatterns.CHAPTER_TITLE,
            "EPILOGUE",
        )
    )

    chapter_titles = re.findall(
        pattern,
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    logging.debug(f"Found chapter titles: {pformat(chapter_titles)}")

    text = re.sub(
        pattern,
        r"{token}\1".format(token=SpecialTokens.START_OF_CHAPTER),
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    return text


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
        RegexPatterns.SENTENCE_SPLITTING,
        SpecialTokens.END_OF_SENTENCE + "\n",
        text,
    )


def add_search_term_tags(text: str) -> str:
    """
    Adds search term tags to the input text.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with search term tags.
    """
    logging.debug("Adding search term tags...")

    for key, pattern in search_terms.build_pattern_map(
        search_terms.book_query_terms
    ).items():
        # add tag after any matches
        text = re.sub(
            pattern,
            r"\1<{tag}>".format(tag=key.upper()),
            text,
            # flags=re.IGNORECASE,
        )

    return text


def preprocess_data(text: str):
    """
    Preprocesses the text.

    Args:
        text (str): The input text.

    Returns:
        str: The preprocessed text.
    """
    logging.info("Preprocessing data...")

    # Initial normalization to help with the rest of the processing
    text = preprocessing.remove_extra_whitespace(text)

    text = extract_body(text)

    # We add chapter delimiter to help split the text into chapters later
    text = add_chapter_delimiter(text)

    # We add sentence delimiter to help split the text into sentences later
    text = preprocessing.join_paragraph_lines(text)

    # Non-destructive normalization/translation from unicode to ascii equivalents
    text = preprocessing.normalize_character_set(text)

    text = add_sentence_delimiter(text)

    text = add_search_term_tags(text)

    return text
