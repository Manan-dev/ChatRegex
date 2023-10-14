import logging
import random
import re
import string
import sys
from enum import Enum

from lib import chat, store, utils
from lib.chat import AIResponse


class RegexPatterns(str, Enum):
    HELP = r"^(help|h)$"
    QUIT = r"^(exit|quit|q)$"
    EXAMPLE = r"^(example(s)?|ex)$"
    FIRST_MENTION = r"first mention (?P<entity>.*)"  # TODO:
    WORDS_AROUND = r"(?P<num_words>\d+) words around (?P<entity>.*)"
    WORDS_COOCCUR = r"cooccur (?P<entity1>.*) and (?P<entity2>.*)"


class ChatBot:
    def __init__(self, data):
        self.data = data

        self.capabilities = {
            # Special Commands
            RegexPatterns.QUIT: self.__cmd_quit,
            RegexPatterns.HELP: self.__cmd_help,
            RegexPatterns.EXAMPLE: self.__cmd_example,
            # Analysis Capabilities
            RegexPatterns.FIRST_MENTION: self.__get_first_mention,
            RegexPatterns.WORDS_AROUND: self.__get_words_around,
            RegexPatterns.WORDS_COOCCUR: self.__get_cooccurance,
        }

    def __fallback(self) -> AIResponse:
        return AIResponse(
            [
                AIResponse(["Sorry", "I'm sorry"], [",", "!"], join=""),
                None,
            ],
            ["I don't understand", "I don't know how to respond to that"],
        )

    def __greet(self) -> AIResponse:
        return chat.AIResponse(
            "Hello!",
            ["What can I do for you?", "How can I help you?"],
        )

    def __cmd_quit(self) -> AIResponse:
        return chat.AIResponse(
            ["Thank you for choosing ChatRegex!", "Sad to see you go :(", None],
            "Goodbye!",
            fn=lambda _: sys.exit(0),
        )

    def __cmd_help(self) -> AIResponse:
        return chat.AIResponse(
            chat.AIResponse(
                ["Here are some", None],
                "special commands",
                ["you can use", None],
                ":",
            ),
            "\n  help, h       - Print this help message",
            "\n  exit, quit, q - Exit the program",
        )

    def __cmd_example(self) -> AIResponse:
        return chat.AIResponse(
            ["Here are some", None],
            "example",
            ["questions", "prompts", "queries"],
            ["you can ask", None],
            ":\n",
            [f'  - "{ex}"' for ex in random.sample(store.example_prompts, 3)],
        )

    def __get_first_mention(self, entity):
        """
        Gets the first mention of a word in the text.
        """
        entity = entity.lower().strip()

        logging.info(f"get_first_mention: entity={entity}")

        response = ""
        try:
            terms = store.search_terms_permutation_map[entity]
            logging.info(f"related search terms: {terms}")

            # TODO: ...
            response = f"{entity} was first mentioned ..."
        except KeyError:
            # TODO: Make this less passive-aggressive
            response = "I am sorry but I have no idea what you're talking about."

        return response

    def __get_words_around(self, num_words, entity):
        logging.debug(f"get_words_around: num_words={num_words}, entity={entity}")

        return "get_words_around"

    def __get_cooccurance(self, entity1, entity2):
        logging.debug(f"get_cooccur: entity1={entity1}, entity2={entity2}")

        return "get_cooccur"

    def start(self, ai_name: str = "AI", user_name: str = "You"):
        name_max_len: int = max(len(ai_name), len(user_name))
        # make the width of the names the same by padding with spaces
        ai_name = ai_name.ljust(name_max_len)
        user_name = user_name.ljust(name_max_len)

        print("=" * 80)

        msg_ai: str = str(self.__greet())
        print(f"{ai_name}: {msg_ai}")
        print("-" * 80)

        while True:
            try:
                msg_usr_orig: str = input(f"{user_name}: ")
            except KeyboardInterrupt:
                msg_usr_orig = "exit"

            msg_usr_proc: str = ChatBot.preprocess_msg(msg_usr_orig)
            logging.debug(f"msg_usr_proc: {msg_usr_proc}")
            if not msg_usr_proc:
                continue

            ai_resp: chat.AIResponse
            # Looping through the regex map
            # The first regex that matches the user message will be used to generate a response
            for cmd, resp in self.capabilities.items():
                match = re.match(cmd, msg_usr_proc, re.IGNORECASE)
                if match:
                    # we pass named capture groups as keyword arguments to the response function
                    # if a function
                    ai_resp = resp(**match.groupdict()) if callable(resp) else resp
                    break
            else:
                ai_resp = self.__fallback()

            logging.debug(f"ai_resp: {ai_resp}")

            ai_resp_final = ChatBot.postprocess_msg(str(ai_resp), use_synonyms=True)

            logging.debug(f"ai_resp_final: {ai_resp_final}")
            print(f"{ai_name}: {ai_resp_final}")
            print("-" * 80)

            # This is primarily for the quit command, which defines fn to exit the program
            if isinstance(ai_resp, chat.AIResponse) and ai_resp.fn is not None:
                ai_resp.fn(ai_resp)

    @staticmethod
    def preprocess_msg(msg: str) -> str:
        # msg = utils.remove_stopwords(msg)
        msg = utils.remove_punctuation(msg)
        msg = utils.remove_extra_whitespace(msg)
        return msg.strip()

    @staticmethod
    def postprocess_msg(msg: str, use_synonyms: bool = False) -> str:
        if use_synonyms:
            # For variety, we can replace some words with synonyms
            msg = utils.create_text_variation(msg)
        # remove spaces before certain punctuation
        msg = re.sub(r"\s+([.,!?;:])", r"\1", msg)
        # capitalize the first letter of the message
        msg = msg[0].upper() + msg[1:]
        # add a period at the end if there isn't any punctuation
        if not re.search(f"[{string.punctuation}]$", msg):
            msg += "."
        return msg.strip()