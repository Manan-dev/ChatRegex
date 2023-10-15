"""
Miscellaneous utility functions that don't fit anywhere else.
"""


import logging
import string


def re_union(*args):
    """
    Creates a regex union of the input arguments.

    Args:
        *args (str): The input strings to be joined.

    Returns:
        str: A regex union of the input strings.
    """
    res = "((" + ")|(".join(list(set(args))) + "))"
    # logging.debug(res)
    return res


def extract_unicode_charset(text: str) -> set[str]:
    """
    Extracts the set of unicode characters from the input text.

    Args:
        text (str): The input text to be processed.

    Returns:
        set[str]: The set of unicode characters in the input text.
    """
    # only unicode characters
    return set(text) - set(string.printable)


def create_permutation_map(lists_of_terms: list[list[str]]):
    """
    Given a list of lists containing alternative words/phrases, create a map
    where each word/phrase is mapped to the entire list of alternatives.
    This can be done once and used for constant-time lookups.
    """
    permutation_map = {}
    for alts in lists_of_terms:
        alts = list(set(map(str.strip, alts)))
        for s in alts:
            permutation_map[s.lower()] = alts

    return permutation_map
