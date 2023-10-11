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
                store.RegexPatterns.Processing.CHAPTER,
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


def mol_processing(text: str):  
    toc_elems = [
            "1 A Fellow Traveller",
            "2 An Appeal for Help",
            "3 At the Villa Genevive",
            "4 The Letter Signed Bella",
            "5 Mrs. Renaulds Story",
            "6 The Scene of the Crime",
            "7 The Mysterious Madame Daubreuil",
            "8 An Unexpected Meeting",
            "9 M. Giraud Finds Some Clues",
            "10 Gabriel Stonor",
            "11 Jack Renauld",
            "12 Poirot Elucidates Certain Points",
            "13 The Girl with the Anxious Eyes",
            "14 The Second Body",
            "15 A Photograph",
            "16 The Beroldy Case",
            "17 We Make Further Investigations",
            "18 Giraud Acts",
            "19 I Use My Grey Cells",
            "20 An Amazing Statement",
            "21 Hercule Poirot on the Case!",
            "22 I Find Love",
            "23 Difficulties Ahead",
            "24 Save Him!",
            "25 An Unexpected Dnouement",
            "26 I Receive a Letter",
            "27 Jack Renaulds Story",
            "28 Journeys End"]

    for elem in toc_elems:
        matches = re. findall(f"^{elem}$", text)
        
        if len(matches) > 2:
            print(f"WARN: Expected 2 matches but got {len(matches)}")
            continue
        
        replacement = f'Chapter {elem}'
        text = re.sub(elem, replacement, text)
    
    return text