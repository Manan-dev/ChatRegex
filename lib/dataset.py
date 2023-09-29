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
    with open(file_path, "r", encoding='ascii', errors='ignore') as f:
        lines = f.readlines()
    
    text = ''.join(map(str,lines))
    return text

