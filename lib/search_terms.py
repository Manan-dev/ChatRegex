import logging
import re

from lib import utils

tag_to_subpatterns = {
    "investigator": [
        "[iI]nvestigator",
        "[dD]etective",
        # Murder on the Links
        "(Hercule )?Poirot",
        # Sign of the Four
        "(Sherlock Holmes)|Holmes",
        # Man in the Brown Suit
        "((Colonel )?Race)|Colonel",
    ],
    "perpetrator": [
        "[pP]erpetrator",
        "[kK]iller",
        "[mM]urderer",
        # Murder on the Links
        "(((Marthe|Madame) )?Daubreuil)|Marthe",
        # Sign of the Four
        "((Jonathan )?Small)|Jonathan",
        # The Man in the Brown Suit
        "(Sir )?Eustace Pedler",
    ],
    "suspect": [
        "[sS]uspect",
        # Murder on the Links
        "Renauld|Jack|Eloise",
        "(M. )?(Lucien )?Bex",
        "((Bella|Dulcie) )?Duveen|Bella|Dulcie|Dulcibella",
        "(Leonie|Denise)( Oulard)?",  # Léonie Oulard
        # Sign of the Four
        "(Major (John )?Sholto)|major",
        "(Captain )?Morstan|Captain",
        "(Thaddeus )?Sholto|Thaddeus",
        "Tonga",
        # The Man in the Brown Suit
        "(Suzanne )?Blair",
        "(Guy )?Pagett",
    ],
    "crime": [
        "[cC]rime",
        "[mM]urder",
        "[kK]ill",
        "[sS]tabbed",
        "[tT]heft",
        "[kK]idnapping",
        "[dD]eception",
        "[bB]lackmail",
    ],
}


tag_to_pattern = {
    k: r"\b({rgx})\b".format(
        rgx=utils.re_union(*list([k] + v)),
    )
    for k, v in tag_to_subpatterns.items()
}


def add_search_term_tags(text: str) -> str:
    """
    Adds search term tags to the input text.

    Args:
        text (str): The input text to be modified.

    Returns:
        str: The modified text with search term tags.
    """
    logging.debug("Adding search term tags...")

    for key, pattern in tag_to_pattern.items():
        # add tag after any matches
        text = re.sub(
            pattern,
            r"\1<{tag}>".format(tag=key.upper()),
            text,
            # flags=re.IGNORECASE,
        )

    return text
