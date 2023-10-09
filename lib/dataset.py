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

    text = "".join(map(str, lines))
    return text


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

    pattern = r"^\*\*\* (?:START|END) OF THE PROJECT GUTENBERG EBOOK [\w ]+ \*\*\*$"

    split_text = re.split(pattern, text, flags=re.MULTILINE)

    if len(split_text) != 3:
        print(
            "WARN: Incorrect number of matches for start/end markers. Returning original text."
        )
        return text

    # Only keep the in-between text
    return "".join(split_text[1:-1]).strip()


def join_paragraph_lines(text):
    """
    Joins lines that are part of the same paragraph.
    This is to fix random newlines in the middle of sentences caused by how the text was originally extracted.
    Parameters:
      text (string): Text to process.
    Returns:
      processed_text (string): Processed text.
    """
    pattern = r"([^\n])\n([^\n])"
    return re.sub(pattern, r"\1 \2", text)


def preprocess_data(text: str):
    print("Processing data...")

    text = utils.remove_extra_whitespace(text)

    text = remove_unwanted_text(text)

    # text = utils.remove_stopwords(text)
    # text = utils.add_sentence_delimiter(text)
    # text = utils.remove_punctuation(text)
    return text
