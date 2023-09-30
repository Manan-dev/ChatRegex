"""
Functions for loading and processing text dataset.    
"""
import os
import re

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
