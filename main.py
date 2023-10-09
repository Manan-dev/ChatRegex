import argparse
import json
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


def main():
    print("=" * 80)
    print(header_text)

    args = parse_args()

    input_path = args.input
    is_debug = args.debug

    # TODO: Error checking if file exists or not a valid text file?
    data = dataset.read_data(input_path)

    # TODO: Data processing
    data_proc = dataset.preprocess_data(data)

    # TODO: Remove this later
    with open(f"{os.path.splitext(input_path)[0]}_proc.txt", "w") as f:
        f.write(data_proc)

    feature_map = dataset.extract_features(data_proc)

    # TODO: Remove this later
    with open(f"{os.path.splitext(input_path)[0]}_features.json", "w") as f:
        f.write(json.dumps(feature_map, indent=4))

    # Chat loop
    chat.start_chat_loop(feature_map)


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
        "-d",
        "--debug",
        action="store_true",
        help="enable debug mode",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
