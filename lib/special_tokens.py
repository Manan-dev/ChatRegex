import re
from enum import Enum


class SpecialTokens(str, Enum):
    START_OF_CHAPTER = "<SOC>"
    END_OF_SENTENCE = "<EOS>"

    def __str__(self) -> str:
        return self.value


def remove_special_tokens(text: str):
    return re.sub(r"<[A-Z]{3,}>", "", text)
