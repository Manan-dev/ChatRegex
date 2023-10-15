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
    # logging.basicConfig(
    #     level=logging.DEBUG,
    #     format="%(levelname)s: %(message)s",
    #     handlers=[
    #         logging.FileHandler("chatregex.log", mode="w"),
    #         CustomStreamHandler(
    #             sys.stdout, level=logging.DEBUG if args.verbose else logging.INFO
    #         ),
    #     ],
    # )
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
          print("A:", ans)
          print("-" * 80)

    # TODO: Add more test cases

    print()
    print("=" * 80)
    run_qa(chat.example_prompts.samples)



    # print()
    # print("=" * 80)
    # questions2 = [
    #     "When do the investigator and perpetrator co-occur?",
    # ]
    # run_qa(questions2)


def main():
    args = parse_args()
    setup_logging(args)

    print("=" * 80)
    print(header_text)

    input_path = args.input
    # TODO: Error checking if file exists or not a valid text file?
    data = dataset.read_data(input_path)

    data_proc = dataset.preprocess_data(data)

    # TODO: Remove this later
    with open(f"{os.path.splitext(input_path)[0]}_proc.txt", "w") as f:
        f.write(data_proc)

    bot = chat.ChatBot(data_proc)

    # TODO: Remove this later
    with open(f"{os.path.splitext(input_path)[0]}_features.json", "w") as f:
        json.dump(bot.data_map, f, indent=4)

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
        help="increase output verbosity",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="test mode",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
