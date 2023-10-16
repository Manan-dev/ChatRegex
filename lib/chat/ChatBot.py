import logging
import random
import re
import string
import sys
from enum import Enum
from pprint import pformat

from lib import preprocessing, search_terms, special_tokens, utils

from . import AIResponse
from .example_prompts import samples


class RegexPatterns(str, Enum):
    """
    This class defines regex patterns used by the chatbot
    for matching user input to commands and analysis queries.
    """

    # Special Commands
    HELP = r"^(help|h)$"

    QUIT = r"^(exit|quit|q)$"

    EXAMPLE = r"^(example(s)?|ex)( (?P<num>\d))?$"

    # Simple Greeting
    GREET = (
        r"^(hi|hello|hey|howdy|greetings|salutations|sup|yo|what's up|what up|wassup)$"
    )

    # Handling first mention queries
    FIRST_MENTION_V1 = r".*({rgx}).*(?P<term>{terms}).*".format(
        rgx=r"(first|initial(ly)?) (meet|appear(s)?|introduce(d)?|enter(s)?|mention(s)?|brought( up)?|disclosed|reveal(s)?|refer(s)?|talk(s)?|hear|time|bring)( possible)?",
        terms=utils.re_union(
            *[
                p
                for p in search_terms.build_pattern_map(
                    search_terms.all_query_terms
                ).values()
            ]
        ),
    )
    FIRST_MENTION_V2 = r".*(?P<term>{terms}).*({rgx}).*".format(
        rgx=r"(first|initial(ly)?) (meet|appear(s)?|introduce(d)?|enter(s)?|mention(s)?|brought( up)?|disclosed|reveal(s)?|refer(s)?|talk(s)?|hear|time|bring)",
        terms=utils.re_union(
            *[
                p
                for p in search_terms.build_pattern_map(
                    search_terms.all_query_terms
                ).values()
            ]
        ),
    )

    # Handling words around queries
    WORDS_AROUND_V1 = r".*({rgx}).*(?P<term>{terms}).*".format(
        rgx=r"surround|accompany|before after|around|near|close to",
        terms=utils.re_union(
            *[
                p
                for p in search_terms.build_pattern_map(
                    search_terms.all_query_terms
                ).values()
            ]
        ),
    )

    WORDS_AROUND_V2 = r".*(?P<term>{terms}).*({rgx}).*".format(
        rgx=r"surround|accompany|before after|around|near|close to",
        terms=utils.re_union(
            *[
                p
                for p in search_terms.build_pattern_map(
                    search_terms.all_query_terms
                ).values()
            ]
        ),
    )

    # Handling co-occurance queries
    WORDS_COOCCUR_V1 = r".*({rgx}).*(?P<term1>{terms}) (?P<term2>{terms}).*".format(
        rgx=r"co[- ]?occur|appear same sentence|both mentioned",
        terms=utils.re_union(
            *[
                p
                for p in search_terms.build_pattern_map(
                    search_terms.all_query_terms
                ).values()
            ]
        ),
    )

    WORDS_COOCCUR_V2 = r".*(?P<term1>{terms}) (?P<term2>{terms}).*({rgx}).*".format(
        rgx=r"co[- ]?occur|appear same sentence|both mentioned",
        terms=utils.re_union(
            *[
                p
                for p in search_terms.build_pattern_map(
                    search_terms.all_query_terms
                ).values()
            ]
        ),
    )

    def __str__(self):
        return self.value


class ChatBot:
    """
    This class defines the chatbot and its capabilities.
    The chatbot is initialized with the preprocessed text data.
    It then builds a data structure to store various information
    to be used for analysis queries.
    """

    def __init__(self, data: str):
        self.data = data
        self.data_map = {}
        self.build_data_map()

        # Maps regex patterns to functions that generate responses
        self.capabilities = {
            # Special Commands
            RegexPatterns.QUIT: self.cmd_quit,
            RegexPatterns.HELP: self.cmd_help,
            RegexPatterns.EXAMPLE: self.cmd_example,
            # Analysis Capabilities
            RegexPatterns.FIRST_MENTION_V1: self.get_first_mention,
            RegexPatterns.FIRST_MENTION_V2: self.get_first_mention,
            RegexPatterns.WORDS_AROUND_V1: self.get_words_around,
            RegexPatterns.WORDS_AROUND_V2: self.get_words_around,
            RegexPatterns.WORDS_COOCCUR_V1: self.get_cooccurance,
            RegexPatterns.WORDS_COOCCUR_V2: self.get_cooccurance,
            # Misc
            RegexPatterns.GREET: self.greet,
        }

    def build_data_map(self):
        """
        Parses the preprocessed text data and stores various information
        for easy lookup later when answering analysis queries.
        """
        # Split the text into chapters
        chapters = self.data.split(special_tokens.SpecialTokens.START_OF_CHAPTER)[1:]

        # Iterate through the chapters to populate the data structure
        for chapter_idx, chapter in enumerate(chapters):
            # Split the chapter into lines
            lines = chapter.splitlines()

            # The first line should be the chapter title
            chapter_title = lines[0].strip()

            # Extract sentences based on <EOS> at the end of lines
            sentences = [
                line.strip()
                for line in lines
                if line.strip().endswith(special_tokens.SpecialTokens.END_OF_SENTENCE)
            ]

            # Iterate through the sentences and look for regex matches
            for sentence_idx, sentence in enumerate(sentences):
                for tag, pattern in search_terms.build_pattern_map(
                    search_terms.book_query_terms
                ).items():
                    tag = tag.lower()

                    if match := re.search(pattern, sentence):
                        occurance = {
                            "matched_term": match.group(),
                            "sentence": special_tokens.remove_special_tokens(
                                sentence,
                            ),
                            "sentence_idx": sentence_idx + 1,
                            "chapter_idx": chapter_idx + 1,
                            "chapter_title": special_tokens.remove_special_tokens(
                                chapter_title
                            ),
                        }

                        if tag not in self.data_map:
                            self.data_map[tag] = {
                                "matched_terms": [tag],
                                "mentions": [],
                            }

                        self.data_map[tag]["matched_terms"] = list(
                            set([match.group()] + self.data_map[tag]["matched_terms"])
                        )
                        self.data_map[tag]["mentions"].append(occurance)

    def fallback(self) -> AIResponse:
        """
        This function is called when the chatbot doesn't understand the user input.
        I.E.: When none of the regex patterns match the user input.
        """
        logging.debug("Falling back to default response...")

        return AIResponse(
            [
                AIResponse(["Sorry", "I'm sorry"], [",", "!"], join=""),
                None,
            ],
            ["I don't understand", "I don't know how to respond to that"],
        )

    def greet(self, msg=None) -> AIResponse:
        """
        This function is called when the user greets the chatbot.
        """
        logging.debug("Greeting user...")

        return AIResponse(
            "Hello!",
            ["What can I do for you?", "How can I help you?"],
        )

    def cmd_quit(self, msg: str) -> AIResponse:
        """
        This function is called when the user wants to quit the program.
        """
        logging.debug("Exiting program...")

        return AIResponse(
            ["Thank you for choosing ChatRegex!", "Sad to see you go :(", None],
            "Goodbye!",
            fn=lambda _: sys.exit(0),
        )

    def cmd_help(self, msg: str) -> AIResponse:
        """
        This function is called when the user wants to print the help message.
        """
        logging.debug("Printing help message...")

        return AIResponse(
            AIResponse(
                ["Here are some", None],
                "special commands",
                ["you can use", None],
                ":",
            ),
            "\n  help, h       - Print this help message",
            "\n  example, ex   - Print some example prompts (e.g. `example` or `example 5` to print 5 examples)",
            "\n  exit, quit, q - Exit the program",
        )

    def cmd_example(self, msg: str, num: int = 1) -> AIResponse:
        """
        This function is called when the user wants to print some example prompts.
        """
        num = num or 1
        logging.debug(f"Printing example prompts ({num})...")

        return AIResponse(
            ["Here are some", None],
            "example",
            ["questions", "prompts", "queries"],
            ["you can ask", None],
            ":\n",
            "\n".join([f'- "{ex}"' for ex in random.sample(samples, int(num))]),
        )

    def find_term_data(self, term: str) -> dict | None:
        """
        Helper function to look up the parsed data for a given term.
        """
        term = term.lower()

        # base case: if we can index directly into the data_map, then we're done
        if term in self.data_map:
            return self.data_map[term]

        result = None
        # otherwise, we need to check if the term is a substring of any of the matched terms
        for _, termdata in self.data_map.items():
            if any(
                term in matched_term.lower() or matched_term.lower() in term
                for matched_term in termdata["matched_terms"]
            ):
                logging.debug(
                    f"find_term_data: `{term}` -> {pformat(termdata, sort_dicts=False)}"
                )

                result = termdata
                break

        return result

    def get_first_mention(self, msg: str, term: str) -> AIResponse | str:
        """
        This function is called when the user wants to find the first mention of a term.
        """
        term = term.lower()

        logging.debug(f"get_first_mention: `{term}`")

        termdata = self.find_term_data(term)

        if termdata is None:
            return f"Sorry, I couldn't find any mentions of `{term}`."
        if re.match(utils.re_union(*search_terms.book_query_terms["suspect"]), term):
            mentions = []
            terms = set()
            for mention in termdata["mentions"]:
                if mention["matched_term"] not in terms:
                    mentions.append(mention)
                    terms.add(mention["matched_term"])

            sentence_list = []
            chapter_title = None
            for mention in mentions:
                if mention["chapter_title"] != chapter_title:
                    sentence_list.extend(
                        [
                            "\n",
                            f"{mention['chapter_title']}, sentence #{mention['sentence_idx']}",
                            f"mentions `{mention['matched_term']}`.",
                        ]
                    )
                else:
                    sentence_list.extend(
                        [
                            AIResponse(
                                ["Next,", "Also,"],
                            ),
                            f"sentence #{mention['sentence_idx']} mentions `{mention['matched_term']}`.",
                        ]
                    )
                chapter_title = mention["chapter_title"]

            return AIResponse(
                [
                    "Let's see...",
                    "Let me see...",
                    "I can do that!",
                    "Alright,",
                    "I can help with that",
                    None,
                ],
                "Here are the mentions of",
                f"`{term}`",
                *sentence_list,
            )

        first_mention = termdata["mentions"][0]

        term_or_alt_str = f"`{term}`"
        # determine whether to add term in parentheses by whether it's a substring of the matched term
        if first_mention["matched_term"].lower() not in term.lower():
            term_or_alt_str = (
                f"{term_or_alt_str} when referring to `{first_mention['matched_term']}`"
            )

        # return pformat(first_mention, sort_dicts=False)
        return AIResponse(
            [
                "Let's see...",
                "Let me see...",
                "Well,",
                "Hmm...",
                "In my analysis,",
                None,
            ],
            ["it looks like", "I see that", "I found that", None],
            # [f"the first mention of `{term}` is in {first_mention['chapter_title']}, sentence #{first_mention['sentence_idx']}",
            [
                AIResponse(
                    "the first",
                    ["related", None],
                    ["mention", "occurrence", "instance"],
                    f"of {term_or_alt_str} is in",
                    [
                        f"{first_mention['chapter_title']}, sentence #{first_mention['sentence_idx']}.",
                        f"sentence #{first_mention['sentence_idx']} of {first_mention['chapter_title']}.",
                    ],
                ),
                AIResponse(
                    [
                        f"{first_mention['chapter_title']}, sentence #{first_mention['sentence_idx']}",
                        f"sentence #{first_mention['sentence_idx']} of {first_mention['chapter_title']}",
                    ],
                    f"contains the first",
                    ["mention", "occurrence", "instance"],
                    f"of {term_or_alt_str}.",
                ),
            ],
        )

    def get_words_around(
        self, msg: str, term: str, num_words_default: int = 3
    ) -> AIResponse | str:
        """
        This function is called when the user wants to find the words around a term on every mention.
        """
        term = term.lower()

        logging.debug(f"get_words_around: `{term}`")

        termdata = self.find_term_data(term)

        if termdata is None:
            return f"Sorry, I couldn't find any mentions of `{term}`."

        mentions_enhanced = []

        for mention in termdata["mentions"]:
            sentence = mention["sentence"]
            matched_term = mention["matched_term"]

            # we split the sentence by the matched term
            # which allows us to get the words at the boundaries
            sentence_parts = sentence.split(matched_term)

            words_around = []

            for i, sentence_part in enumerate(sentence_parts):
                # some processing
                sentence_part = preprocessing.remove_stopwords(sentence_part)
                sentence_part = preprocessing.remove_punctuation(sentence_part)
                sentence_part = preprocessing.remove_extra_whitespace(sentence_part)

                sentence_parts[i] = sentence_part
                words = sentence_part.split()

                if i == 0:
                    # first part - only get the last num_words
                    words_around.extend(words[-min(num_words_default, len(words)) :])
                elif i == len(sentence_parts) - 1:
                    # last part - only get the first num_words
                    words_around.extend(words[: min(num_words_default, len(words))])
                else:
                    # middle part - get both the first and last num_words
                    words_around.extend(words[-min(num_words_default, len(words)) :])
                    words_around.extend(words[: min(num_words_default, len(words))])

            # removing duplicates
            words_around = list(set(words_around))

            # remove falsey values like empty strings
            words_around = [w for w in words_around if w]

            # remove any single-letter words
            words_around = [w for w in words_around if len(w) > 1]

            # if empty safe to skip
            if not words_around:
                continue

            # remove any numbers
            words_around = [w for w in words_around if not w.isdigit()]

            mentions_enhanced.append(
                {
                    **mention,
                    "sentence_parts": sentence_parts,
                    "words_around": words_around,
                }
            )

        # return pformat(mentions_enhanced, sort_dicts=False)

        wa = AIResponse(
            [
                "the words are:",
                AIResponse(["we see:", "we have:"]),
                "they are:",
            ]
        )
        sentence_list = []
        last_chapter = None

        for mention in mentions_enhanced:
            words_around_str = f"`{'`, `'.join(mention['words_around'])}`"
            if words_around_str == "``":
                continue
            if mention["chapter_title"] != last_chapter:
                sentence_list.extend(
                    [
                        "\n",
                        f"In {mention['chapter_title']}, sentence #{mention['sentence_idx']},",
                        wa,
                        f"{words_around_str}.",
                    ]
                )
            else:
                sentence_list.extend(
                    [
                        f"Next, in sentence #{mention['sentence_idx']},",
                        wa,
                        f"{words_around_str}.",
                    ]
                )
            last_chapter = mention["chapter_title"]

        return AIResponse(
            "Here are the words around",
            f"`{term}`",
            "on",
            ["each", "every"],
            "mention:",
            *sentence_list,
        )

    def get_cooccurance(self, msg: str, term1: str, term2: str) -> AIResponse | str:
        """
        This function is called when the user wants to find the co-occurance of two terms.
        """
        term1, term2 = term1.lower(), term2.lower()

        logging.debug(f"get_cooccurance: `{term1}`, `{term2}`")

        term1data = self.find_term_data(term1)
        term2data = self.find_term_data(term2)

        if term1data is None:
            return f"Sorry, I couldn't find any mentions of `{term1}`."

        if term2data is None:
            return f"Sorry, I couldn't find any mentions of `{term2}`."

        co_occurrences_list = []

        for mention1 in term1data["mentions"]:
            for mention2 in term2data["mentions"]:
                if mention1["chapter_idx"] != mention2["chapter_idx"]:
                    continue

                if mention1["sentence_idx"] != mention2["sentence_idx"]:
                    continue

                co_occurrences_list.append(
                    {
                        "chapter_title": mention1["chapter_title"],
                        "chapter_idx": mention1["chapter_idx"],
                        "sentence_idx": mention1["sentence_idx"],
                        "sentence": mention1["sentence"],
                        "matched_term1": mention1["matched_term"],
                        "matched_term2": mention2["matched_term"],
                    }
                )

        # return pformat(co_occurrences_list, sort_dicts=False)

        sentence_list = []
        last_chapter = None

        for co_occurrence in co_occurrences_list:
            both_terms_Str = f"`{co_occurrence['matched_term1']}` and `{co_occurrence['matched_term2']}`"

            random_sentence_position = AIResponse(
                [
                    f"sentence #{co_occurrence['sentence_idx']} mentions both {both_terms_Str}.",
                    f"{both_terms_Str} are mentioned in sentence #{co_occurrence['sentence_idx']}.",
                ]
            )

            if co_occurrence["chapter_title"] != last_chapter:
                sentence_list.extend(
                    [
                        "\n",
                        f"In {co_occurrence['chapter_title']},",
                        random_sentence_position,
                    ]
                )
            else:
                sentence_list.extend(
                    [
                        AIResponse(["Next,", "Also,"]),
                        random_sentence_position,
                    ]
                )
            last_chapter = co_occurrence["chapter_title"]

        return AIResponse(
            "Here are the co-occurrences of",
            f"`{term1}`",
            "and",
            f"`{term2}`",
            "on each mention:",
            *sentence_list,
        )

    def answer(self, msg: str) -> AIResponse | None:
        """
        Given a user message, this function will try to generate a response.
        If no response can be generated, it will return None.
        The None can be used to trigger a fallback response.
        """
        msg_usr_proc: str = ChatBot.preprocess_msg(msg)

        if not msg_usr_proc:
            logging.debug("Empty message, skipping...")
            return None

        ai_resp = None
        # Looping through the regex map
        # The first regex that matches the user message will be used to generate a response
        for cmd, resp in self.capabilities.items():
            if match := re.match(cmd, msg_usr_proc, re.IGNORECASE):
                # we can pass named capture groups as keyword arguments to the response function

                ai_resp = resp(msg, **match.groupdict()) if callable(resp) else resp

                break

        return ai_resp

    def start(self, ai_name: str = "AI", user_name: str = "You"):
        """
        This function starts the interactive chat session (chat loop)
        which will prompt the user for input and generate a response.
        """
        logging.info("Starting interactive chat session...")

        # make the width of the names the same by padding with spaces
        name_max_len: int = max(len(ai_name), len(user_name))
        ai_name = ai_name.ljust(name_max_len)
        user_name = user_name.ljust(name_max_len)

        print("=" * 80)

        msg_ai: str = str(self.greet())
        print(f"{ai_name}: {msg_ai}")
        print("-" * 80)

        # the main chat loop
        while True:
            # capture user input
            try:
                msg_usr_orig: str = input(f"{user_name}: ")
            except KeyboardInterrupt:
                msg_usr_orig = "exit"

            # get the AI's response
            ai_resp = self.answer(msg_usr_orig)
            if ai_resp is None:
                ai_resp = self.fallback()

            # final post-processing of the AI's response
            ai_resp_final = ChatBot.postprocess_msg(str(ai_resp), use_synonyms=True)
            print(f"{ai_name}: {ai_resp_final}")
            print("-" * 80)

            # This is primarily for the quit command, which defines fn to exit the program
            if isinstance(ai_resp, AIResponse) and ai_resp.fn is not None:
                ai_resp.fn(ai_resp)

    @staticmethod
    def preprocess_msg(msg: str) -> str:
        """
        Preprocessing for the user message.
        This is used to standardize the user input before matching it to regex patterns.
        """
        logging.debug(f"before: {msg}")

        msg = preprocessing.remove_stopwords(msg)
        msg = preprocessing.remove_punctuation(msg)
        msg = preprocessing.remove_extra_whitespace(msg)

        msg = msg.strip()

        logging.debug(f"after: {msg}")
        return msg

    @staticmethod
    def postprocess_msg(msg: str, use_synonyms: bool = False) -> str:
        """
        Postprocessing for the AI's response.
        This can create variations in the AI's response to make it seem more natural,
        such as by replacing words with synonyms and certain phrases with alternatives.
        Also enforce some rules like capitalizing the first letter of the response.
        """
        logging.debug(f"before: {msg}")

        # For variety, we can replace some words/phrases with common alternatives
        if use_synonyms:
            msg = AIResponse.create_variation(msg)

        # remove spaces before certain punctuation
        msg = re.sub(r"\s+([.,!?;:])", r"\1", msg)

        # capitalize the first letter of the message
        msg = msg[0].upper() + msg[1:]

        # add a period at the end if there isn't any punctuation at the end
        if not re.search(f"[{string.punctuation}]$", msg):
            msg += "."

        msg = msg.strip()
        logging.debug(f"after: {msg}")
        return msg
