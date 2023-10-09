"""
Functions for loading and processing text dataset.    
"""
import os
import re

from lib import utils


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


def remove_unwanted_text(text):
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

    # Only keep the in-between text
    return "".join(split_text[1:-1]).strip()


def preprocess_data(text: str):
    print("Processing data...")

    # text = remove_unwanted_text(text)

    text = utils.join_paragraph_lines(text)

    text = utils.remove_extra_whitespace(text)

    return text
