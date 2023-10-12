"""
For storing regex expressions, lists of synonyms, and other stuff.
"""

from enum import Enum


class RegexPatterns:
    class Processing(str, Enum):
        # Source: https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch06s09.html
        ROMAN_NUMERALS = r"(?=[MDCLXVI])M*(?:C[MD]|D?C*)(?:X[CL]|L?X*)(?:I[XV]|V?I*)"
        CHAPTER = r"(^(chapter|part) (?:\d{1,3}|" + ROMAN_NUMERALS + r")(?:[.,]? .*)?)$"
        TOC = r"(^Contents\n+(?:.*\n)+?$\n\n)"
    
    class Chat(str, Enum):
        CMD_HELP = r"^(help|h)$"
        CMD_QUIT = r"^(exit|quit|q)$"
        CMD_EXAMPLE = r"^(example(s)?|ex)$"


def create_alternatives_map(alternatives):
    """
    Given a list of lists containing alternative words/phrases, create a map
    where each word/phrase is mapped to the entire list of alternatives.
    This can be done once and used for constant-time lookups.
    """
    alternatives_map = {}
    for alternatives in alternatives:
        alternatives = list(set(map(str.strip, alternatives)))
        for s in alternatives:
            alternatives_map[s] = alternatives
    return alternatives_map


search_term_alts = [
    [
        "investigator",
        "detective",
        # Murder on the Links
        "Hercule Poirot",
        # Sign of the Four
        "Sherlock Holmes",
        # Man in the Brown Suit
        "Colonel Race",
    ],
    [
        "perpetrator",
        "killer",
        "murderer",
        "criminal",
        # Murder on the Links
        "Marthe",
        "Marthe Daubreuil",
        # Sign of the Four
        "Jonathan Small",
        # The Man in the Brown Suit
        "Sir Eustace Pedler",
    ],
    [
        "suspect",
        # Murder on the Links
        "Jack Renauld",
        "Eloise Renauld",
        "M. Bex",
        "Lucien Bex",
        "Bella Duveen",
        "Leonie Oulard",  # Léonie Oulard
        "Denise Oulard",
        # Sign of the Four
        "Major Sholto",
        "Captain Morstan",
        "Thaddeus Sholto",
        "Tonga",
        # The Man in the Brown Suit
        "Suzanne Blair",
        "Guy Pagett",
    ],
    [
        "victim",
        # Murder of the Links
        "M. Paul Renauld",
        "M. Renauld",
    ],
    [
        "crime",
        "murder",
        "kill",
        "stabbed",
        "theft",
        "kidnapping",
        "deception",
        "blackmail",
    ],
]

search_terms_alts_map = create_alternatives_map(search_term_alts)

response_phrase_alts = [
    ["hello!", "hi!", "hey!", "hey there!", "howdy!"],
    ["goodbye", "bye", "adios", "farewell"],
    ["respond to that", "answer that", "reply to that"],
    ["I'm sorry", "I apologize"],
    ["thanks", "thank you"],
    ["can I", "could I", "may I"],
    ["I'm", "I am"],
    ["don't", "do not"],
]
response_phrase_alts_map = create_alternatives_map(response_phrase_alts)

# print("Alternatives Map:")
# for k, v in alternatives_map.items():
#     print(f"{k}: {v}")

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
