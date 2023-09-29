"""
Functions for loading and processing text dataset.    
"""
import os
import re

"""
  Removes all non-ascii characters from the text.
  Parameters:
    text(string): Text to be converted.
  Returns:
    text (string): converted text.
"""
def convert_text_to_ascii(text):
    return text.encode("ascii", "ignore").decode()

"""
  Reads the text file and returns a list of lines.
  Parameters:
    name_of_file (string): Name of the file to be read.
  Returns:
    text (string): Text read from the file.
"""
def read_data(name_of_file):
    file_path = os.path.join("dataset", name_of_file)
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    text = ''.join(map(str,lines))
    text = convert_text_to_ascii(text)
    return text

