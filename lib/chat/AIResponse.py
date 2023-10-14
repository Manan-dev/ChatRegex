import logging
import random
import re
import string
import sys

from lib import store, utils
from lib.store import RegexPatterns


class AIResponse:
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
