"""
For storing regex expressions, lists of synonyms, and other stuff.
"""

import logging
from enum import Enum

from lib import utils

search_terms_map = {
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
        "[cC]riminal",
        # Murder on the Links
        "((Marthe )?Daubreuil)|Marthe",
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
    "victim": [
        "victim",
        # Murder of the Links
        "M. Paul Renauld",
        "M. Renauld",
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


class RegexPatterns:
    class Processing(str, Enum):
        DELIM_PROJ_GUTENBERG = (
            r"^\s*\*\*\* (?:START|END) OF THE PROJECT GUTENBERG EBOOK [\w ]+ \*\*\*$"
        )

        # Source: https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch06s09.html
        ROMAN_NUMERALS = (
            r"(?=[MDCLXVI])"
            r"M*(?:C[MD]|D?C*)"
            r"(?:X[CL]|L?X*)"
            r"(?:I[XV]|V?I*)"  # noqa: E501
        )
        CHAPTER_TITLE = (
            r"(?:chapter|part) (?:\d{1,3}|"
            + ROMAN_NUMERALS
            + r")(?:\.? .*?)?"  # noqa: E501
        )

        TABLE_OF_CONTENTS = r"(^Contents\n+(?:.*\n)+?$\n\n)"

        SENTENCE_SPLITTING = (
            r"(?<!\w\.\w.)"
            # Don't match abbreviations like ["U. S.", "U. K."]
            r"(?<![A-Z]\.)"
            # Don't match 2-letter abbreviations like ["Mr.", "Ms.", "Dr."]
            r"(?<!(Mr|Ms|Dr|Sr|Jr|St|Lt|Co|Mt)\.)"
            # Don't match 3-letter abbreviations like ["Mrs.", "Rev.", "Col."]
            r"(?<!(Mrs|Rev|Col|Maj|Gen|Sgt)\.)"
            r"(?<!(\,\"))"
            r"(((?<=(\.|\!|\?|:))\s)|"
            r"((?<=(\.[\"\']|\![\"\']))\s)|"
            r"((?<=(\"|\'))\n))"  # noqa: E501
        )
        # Note: previous versions, keeping them commented out for reference
        # SENTENCE_SPLITTING = r"(?<=[.!?])\s+"
        # SENTENCE_SPLITTING = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"
        # SENTENCE_SPLITTING = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|:|\"|\!)\s"

        def __str__(self) -> str:
            return self.value


class SpecialTokens(str, Enum):
    START_OF_CHAPTER = "<SOC>"
    END_OF_SENTENCE = "<EOS>"

    def __str__(self) -> str:
        return self.value


# search_terms_alts_map = create_alternatives_map(search_term_alts)

response_phrase_alts = [
    ["hello!", "hi!", "hey!", "hey there!", "howdy!"],
    ["goodbye", "bye", "adios", "farewell"],
    ["respond to that", "answer that", "reply to that"],
    ["I'm sorry", "I apologize"],
    ["thanks", "thank you"],
    ["can I", "could I", "may I"],
    ["I'm", "I am"],
    ["don't", "do not"],
    # ["investigator", "detective"],
    # ["perpetrator", "killer", "murderer", "criminal"],
]

response_phrase_permutation_map = utils.create_permutation_map(response_phrase_alts)


stop_words = [
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "her",
    "hers",
    "herself",
    "it",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
    "what",
    "which",
    "who",
    "whom",
    "this",
    "that",
    "these",
    "those",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "a",
    "an",
    "the",
    "and",
    "but",
    "if",
    "or",
    "because",
    "as",
    "until",
    "while",
    "of",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "s",
    "t",
    "can",
    "will",
    "just",
    "don",
    "should",
    "now",
]

example_prompts = [
    # 1. First Appearance of the Investigator(s)
    "When do we first meet the investigator in the story?",
    "Identify the chapter and sentence where the detective first appears.",
    "Tell me when the investigator is first introduced in the narrative.",
    "In which chapter and sentence is the detective first mentioned?",
    "When does the character of the investigator first enter the plot?",
    # 2. First Mention of the Crime
    "When is the crime first brought up in the novel?",
    "Identify the chapter and sentence where the crime is first mentioned.",
    "At what point is the crime first disclosed?",
    "Tell me when the novel first talks about the crime.",
    "In which chapter and sentence does the narrative first reveal the crime?",
    # 3. First Mention of the Perpetrator
    "When do we first hear about the perpetrator in the story?",
    "Point out the chapter and sentence where the perpetrator is initially mentioned.",
    "When does the narrative first refer to the wrongdoer?",
    "Identify when the perpetrator is first introduced.",
    "Tell me when the criminal is first mentioned in the book.",
    # 4. Words Surrounding the Perpetrator
    "What words frequently surround the perpetrator's mentions?",
    "Identify the three words before and after each mention of the perpetrator.",
    "Which words appear around the perpetrator's name?",
    "Describe the words that often accompany mentions of the perpetrator.",
    "What are the words flanking the perpetrator each time they're mentioned?",
    # 5. Co-occurrence of Detectives and Perpetrators
    "When do the investigator and perpetrator appear in the same scene?",
    "Identify chapters and sentences where the detective and criminal are both mentioned.",
    "Tell me the instances where the detective and perpetrator are together.",
    "When do the investigator and the perpetrator cross paths in the narrative?",
    "In which chapters and sentences do the detective and perpetrator co-occur?",
    # 6. Introduction of Other Suspects
    "When are other suspects first brought into the story?",
    "Identify the chapter and sentence where alternative suspects are introduced.",
    "Tell me when the novel first mentions other possible perpetrators.",
    "When are additional suspects first introduced?",
    "In which chapter and sentence does the story first bring in other suspects?",
]
