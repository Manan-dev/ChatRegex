"""
Functions for loading and processing text dataset.    
"""
import os
import re

from lib import utils

"""
  Reads the text file and returns a list of lines.
  Parameters:
    file_path (string): Path to the file to read.
  Returns:
    text (string): Text read from the file.
"""


def read_data(file_path):
    print(f"Reading data: {file_path}")
    with open(file_path, "r", encoding="ascii", errors="ignore") as f:
        lines = f.readlines()

    text = "".join(map(str, lines))
    return text

"""
  Filters out text between 'START OF THE PROJECT' and 'END OF THE PROJECT'.
  Parameters:
    text (string): Text to filter.
  Returns:
    filtered_text (string): Filtered text.
"""
def remove_unwanted_text(text):
    pattern = r"(START OF THE PROJECT[^\n]*\n)(.*)(END OF THE PROJECT)"
    match = re.search(pattern, text, re.DOTALL)

    if match:
      filtered_text = match.group(2).strip()
    else:
      filtered_text = text

    return filtered_text

def process_data(text: str):
    print(f"Processing data...")
    # TODO: Implement this function
    # Should return some sort of data structure/class that contains the processed form of the data

def process_text(text: str) -> str:
    text = utils.remove_non_printable_characters(text)
    text = utils.remove_stopwords(text)
    text = utils.add_sentence_delimiter(text)
    text = utils.remove_punctuation(text)
    text = utils.remove_extra_spaces(text)
    return text