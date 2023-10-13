"""
Functions for loading and processing text dataset.    
"""
import logging
import re
from pprint import pformat, pprint

from lib import utils
from lib.store import RegexPatterns, SpecialTokens, search_term_map


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

    split_text = re.split(
        RegexPatterns.Processing.DELIM_PROJ_GUTENBERG, text, flags=re.MULTILINE
    )

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
        RegexPatterns.Processing.CHAPTER_TITLE,
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
        RegexPatterns.Processing.TABLE_OF_CONTENTS,
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
            RegexPatterns.Processing.TABLE_OF_CONTENTS,
            "",
            text,
            flags=re.MULTILINE,
        )
        text = normalize_chapter_headings(text, toc_elems)

    text = re.sub(
        r"({rgx})".format(
            rgx=utils.re_union(
                "PROLOGUE",
                RegexPatterns.Processing.CHAPTER_TITLE,
                "EPILOGUE",
            )
        ),
        r"{token}\1".format(token=SpecialTokens.START_OF_CHAPTER),
        text,
        flags=re.MULTILINE | re.IGNORECASE,
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
    text = utils.remove_extra_whitespace(text)

    text = extract_body(text)

    # We add chapter delimiter to help split the text into chapters later
    text = add_chapter_delimiter(text)

    # We add sentence delimiter to help split the text into sentences later
    # text = utils.join_paragraph_lines(text)

    # Non-destructive normalization/translation from unicode to ascii equivalents
    text = utils.normalize_character_set(text)

    text = utils.add_sentence_delimiter(text)

    text = utils.add_search_term_tags(text, search_term_map)

    # TODO: Re-add removal of stop words later after verifying feature extraction
    # TODO: Re-add removal of punctuation later after verifying feature extraction

    return text


def extract_features(text: str):
    logging.info("Extracting features...")

    # Split by chapter delimiter
    split_text = re.split(
        SpecialTokens.START_OF_CHAPTER,
        text,
    )

    # Save stuff to dict
    # TODO: This is only a template and incomplete.
    # TODO: We need to add the stuff more of the stuff we discussed at the last meeting, but this is a start.
    feature_map = {
        "num_chapters": len(split_text),
        "chapter_list": None,
    }

    # ============================================
    # Drill down: Split chapters into paragraphs
    chapter_list = []
    for chapter_text in split_text:
        chapter_lines = chapter_text.strip().splitlines()
        chapter_title = chapter_lines[0]
        chapter_paragraphs = chapter_lines[1:]

        # strip out each paragraph and filter out empty ones
        chapter_paragraphs = list(filter(None, map(str.strip, chapter_paragraphs)))

        feature_map[chapter_title] = {
            "chapter_title": chapter_title,
            "num_paragraphs": len(chapter_paragraphs),
            "paragraph_list": None,
        }

        # ----------------------------------------
        # Drill down: Split paragraphs into sentences
        paragraph_list = []
        for paragraph in chapter_paragraphs:
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)

            paragraph_list.append(
                {
                    "num_sentences": len(sentences),
                    "sencence_list": sentences,
                }
            )
        feature_map[chapter_title]["paragraph_list"] = paragraph_list
        # ----------------------------------------

        chapter_list.append(feature_map[chapter_title])

    feature_map["chapter_list"] = chapter_list

    return feature_map
