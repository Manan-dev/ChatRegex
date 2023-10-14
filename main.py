import argparse
import json
import logging
import os
import sys

from lib import chat, dataset

header_text = """
 ██████╗██╗  ██╗ █████╗ ████████╗   ██████╗ ███████╗ ██████╗ ███████╗██╗  ██╗
██╔════╝██║  ██║██╔══██╗╚══██╔══╝   ██╔══██╗██╔════╝██╔════╝ ██╔════╝╚██╗██╔╝
██║     ███████║███████║   ██║█████╗██████╔╝█████╗  ██║  ███╗█████╗   ╚███╔╝ 
██║     ██╔══██║██╔══██║   ██║╚════╝██╔══██╗██╔══╝  ██║   ██║██╔══╝   ██╔██╗ 
╚██████╗██║  ██║██║  ██║   ██║      ██║  ██║███████╗╚██████╔╝███████╗██╔╝ ██╗
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
"""


class CustomStreamHandler(logging.StreamHandler):
    def __init__(self, stream=None, level=logging.DEBUG):
        super().__init__(stream=stream)
        self.level = level

    def emit(self, record):
        if record.levelno >= self.level:
            super().emit(record)


def setup_logging(args):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler("chatregex.log", mode="w"),
            CustomStreamHandler(
                sys.stdout, level=logging.DEBUG if args.verbose else logging.INFO
            ),
        ],
    )


def main():
    args = parse_args()
    setup_logging(args)

    print("=" * 80)
    print(header_text)

    input_path = args.input
    # TODO: Error checking if file exists or not a valid text file?
    data = dataset.read_data(input_path)

    # TODO: Data processing
    data_proc = dataset.preprocess_data(data)

    # TODO: Remove this later
    with open(f"{os.path.splitext(input_path)[0]}_proc.txt", "w") as f:
        f.write(data_proc)

    bot = chat.ChatBot(data_proc)
    bot.start()


def parse_args():
    parser = argparse.ArgumentParser(description="ChatRegex")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="path to input text file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="increase output verbosity",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
