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


def setup_logging(args):
    # get the logger
    logger = logging.getLogger()
    logger.handlers = []
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.FileHandler("chatregex.log", mode="w")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(levelname)s (%(funcName)s): %(message)s"))
    logger.addHandler(fh)

    # Stream handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(ch)


def run_tests(bot):
    def run_qa(qs):
        for q in qs:
            ans = bot.answer(q)
            print("Q:", q)
            assert ans, "Test case FAILED!!!!"
            print("A:", bot.postprocess_msg(str(ans), use_synonyms=True))
            print("-" * 80)

    print()
    print("=" * 80)
    run_qa(chat.example_prompts.samples)


def main():
    args = parse_args()
    setup_logging(args)

    print("=" * 80)
    print(header_text)

    input_path = args.input
    # TODO: Error checking if file exists or not a valid text file?
    data = dataset.read_data(input_path)

    data_proc = dataset.preprocess_data(data)

    # with open(f"{os.path.splitext(input_path)[0]}_proc.txt", "w") as f:
    #     f.write(data_proc)

    bot = chat.ChatBot(data_proc)

    # with open(f"{os.path.splitext(input_path)[0]}_features.json", "w") as f:
    #     json.dump(bot.data_map, f, indent=4)

    if args.test:
        run_tests(bot)
        return

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
        help="increase console output verbosity",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="disables the interactive chat mode and runs a series of example prompt test cases",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
