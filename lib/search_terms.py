
from lib import utils

book_query_terms = {
    "investigator": [
        "[iI]nvestigator(s)?",
        "[dD]etective(s)?",
        # Murder on the Links
        "(Hercule )?Poirot",
        # Sign of the Four
        "(Sherlock Holmes)|Holmes",
        # Man in the Brown Suit
        "((Colonel )?Race)|Colonel",
    ],
    "perpetrator": [
        "[pP]erpetrator(s)?",
        "[kK]iller(s)?",
        "[mM]urderer(s)?",
        # Murder on the Links
        "(((Marthe|Madame) )?Daubreuil)|Marthe",
        # Sign of the Four
        "((Jonathan )?Small)|Jonathan",
        # The Man in the Brown Suit
        "(Sir )?Eustace Pedler",
    ],
    "suspect": [
        "[sS]uspect(s)?",
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
        "They have robbed him of the treasure",
        "(?<=stone dead, )stabbed in the back",
        "(?<=discovered yesterday, )strangled",
    ],
}

chat_query_terms = {
    "perpetrator": ["bad guy", "villain", "criminal"],
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

all_query_terms = {k: [*v] for k, v in book_query_terms.items()}


for k, v in chat_query_terms.items():
    all_query_terms[k].extend(v)


def build_pattern_map(sub_patterns_map: dict[str, list]):
    pattern_map = {}
    for k, v in sub_patterns_map.items():
        pattern_map[k] = r"\b({rgx})\b".format(
            rgx=utils.re_union(*v),
        )

    return pattern_map
