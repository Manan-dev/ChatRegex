"""
Functions for loading and processing text dataset.    
"""
import os
import re
from pprint import pprint

from lib import store, utils


def read_data(file_path):
    """
    Reads the text file and returns a list of lines.
    Parameters:
      file_path (string): Path to the file to read.
    Returns:
      text (string): Text read from the file.
    """
    print(f"Reading data: {file_path}")
    with open(file_path, "r", encoding="ascii", errors="ignore") as f:
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

    pattern = r"^\s*\*\*\* (?:START|END) OF THE PROJECT GUTENBERG EBOOK [\w ]+ \*\*\*$"

    split_text = re.split(pattern, text, flags=re.MULTILINE)

    print(f"Split text: {len(split_text)}")
    if len(split_text) != 3:
        print(
            "WARN: Incorrect number of matches for start/end markers. Returning original text."
        )
        return text

    _, body_text, _ = split_text

    return body_text.strip()


def preprocess_data(text: str):
    """
    Preprocesses the text.

    Args:
        text (str): The input text.

    Returns:
        str: The preprocessed text.
    """
    print("Preprocessing data...")

    text = utils.remove_extra_whitespace(text)

    text = extract_body(text)

    text = utils.join_paragraph_lines(text)

    # TODO: Re-add removal of stop words later after verifying feature extraction
    # TODO: Re-add removal of punctuation later after verifying feature extraction

    return text


def extract_features(text: str):
    print("Extracting features...")

    # TODO: Doesn't handle The Murder on the Links

    # We add chapter delimiter to help split
    text = re.sub(
        r"^({rgx})$".format(
            rgx=utils.re_union(
                "PROLOGUE",
                store.RegexPatterns.CHAPTER,
                "EPILOGUE",
            )
        ),
        r"<CHAPTER_START>\n\1",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    # Split by chapter delimiter
    split_text = re.split(
        "<CHAPTER_START>",
        text,
    )

    print(f"Split text: {len(split_text)}")

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
        print(chapter_title)

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
