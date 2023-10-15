import random
import re

from lib import utils

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

    @staticmethod
    def create_variation(text: str) -> str:
        """
        Replaces words in the input text with synonyms from a predefined list of alternatives.

        Args:
            text (str): The input text to be modified.

        Returns:
            str: The modified text with replaced synonyms.
        """
        for synonym, synonym_list in response_phrase_permutation_map.items():

            def get_replacement(match):
                """
                Returns a random synonym for the matched word in the input string.

                Args:
                    match (re.Match): A match object containing the word to be replaced.

                Returns:
                    str: A randomly chosen synonym for the matched word, with the same casing as the original word.
                """
                original = match.group(0)

                rnd_synonym = random.choice(synonym_list)

                # Preserve the original casing
                if original.islower():
                    rnd_synonym = rnd_synonym.lower()
                elif original.isupper():
                    rnd_synonym = rnd_synonym.upper()
                elif original.istitle():
                    rnd_synonym = rnd_synonym.title()

                return rnd_synonym

            text = re.sub(
                r"\b" + synonym + r"\b",
                get_replacement,
                text,
                flags=re.IGNORECASE,
            )
        return text
