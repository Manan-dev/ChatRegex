"""
Functions related to the chatbot, including:
- chat loop
- prompt processing/parsing
- response generation
"""


import random
import re
import string
import sys

from lib import store, utils
from lib.store import RegexPatterns


class AIResp:
    """
    Message builder used to easily create messages with some variety.
    Any amount of arguments can be passed to the constructor.
    Arguments can be strings or lists of strings.
    Using lists allows for random selection of a string from the list, to add .
    Any falsey value (like None or empty string) will be skipped.

    Example:
    ```
    builder = MsgBuilder("Hello.", ["How are you?", "How are you doing?", None])
    msg1 = str(builder)
    msg2 = str(builder)
    msg3 = str(builder)
    print(f"msg1: {msg1}")
    print(f"msg2: {msg2}")
    ```

    Potential Output:
    ```
    msg1: Hello. How are you?
    msg2: Hello.
    msg3: Hello. How are you doing?
    ```
    """

    def __init__(self, *msg_parts, join: str = " ", fn=None):
        self.msg_parts = msg_parts
        self.join: str = join
        self.fn = fn

    def __str__(self) -> str:
        parts = []
        for p in self.msg_parts:
            if isinstance(p, str):
                # Skip anything that evaluates to False like empty strings, None, etc.
                if not p:
                    continue
                parts.append(p)
            elif isinstance(p, list):
                # Skip anything that evaluates to False like empty strings, None, etc.
                rnd_msg = random.choice(p)
                if not rnd_msg:
                    continue
                parts.append(str(rnd_msg))
            elif isinstance(p, self.__class__):
                parts.append(str(p))
            else:
                raise TypeError(f"Invalid type: {type(p)}")

        return self.join.join(parts)


resp_greet = AIResp(
    "Hello!",
    ["What can I do for you?", "How can I help you?"],
)

resp_fallback = AIResp(
    [
        AIResp(["Sorry", "I'm sorry"], [",", "!"], join=""),
        None,
    ],
    ["I don't understand", "I don't know how to respond to that"],
)

resp_map = {
    # Special Commands
    RegexPatterns.CMD_QUIT: AIResp(
        ["Thank you for choosing ChatRegex!", "Sad to see you go :(", None],
        "Goodbye!",
        fn=lambda _: sys.exit(0),
    ),
    RegexPatterns.CMD_HELP: AIResp(
        AIResp(
            ["Here are some", None],
            "special commands",
            ["you can use", None],
            ":",
        ),
        "\n  help, h       - Print this help message",
        "\n  exit, quit, q - Exit the program",
    ),
    RegexPatterns.CMD_EXAMPLE: AIResp(
        ["Here are some", None],
        "example",
        ["questions", "prompts", "queries"],
        ["you can ask", None],
        ":\n",
        [f'  - "{ex}"' for ex in random.sample(store.example_prompts, 3)],
    ),
    # TODO: Add regex and responses here
}


def preprocess_msg(msg: str) -> str:
    msg = utils.remove_stopwords(msg)
    msg = utils.remove_punctuation(msg)
    msg = utils.remove_extra_whitespace(msg)
    return msg.strip()


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


def start_chat_loop(feature_map, ai_name: str = "AI", user_name: str = "You"):
    name_max_len: int = max(len(ai_name), len(user_name))
    # make the width of the names the same by padding with spaces
    ai_name = ai_name.ljust(name_max_len)
    user_name = user_name.ljust(name_max_len)

    print("=" * 80)

    msg_ai: str = str(resp_greet)
    print(f"{ai_name}: {msg_ai}")
    print("-" * 80)

    while True:
        msg_usr_orig: str = input(f"{user_name}: ")

        msg_usr_proc: str = preprocess_msg(msg_usr_orig)
        # print(f"msg_usr_proc: {msg_user_proc}")
        if not msg_usr_proc:
            continue

        ai_resp: AIResp
        # Looping through the regex map
        # The first regex that matches the user message will be used to generate a response
        for cmd, resp in resp_map.items():
            if re.match(cmd, msg_usr_proc):
                ai_resp = resp
                break
        else:
            ai_resp = resp_fallback

        print(f"{ai_name}: {postprocess_msg(str(ai_resp), use_synonyms=True)}")
        print("-" * 80)

        # This is primarily for the quit command, which defines fn to exit the program
        if ai_resp.fn is not None:
            ai_resp.fn(ai_resp)
