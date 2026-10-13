"""
Kafka stream producer entrypoint.

The API starts this file with:
python3 src/kafka/stream_producer.py --batch-size 5

The actual streaming logic is reused from producer.py.
"""

import argparse

from producer import stream_data


def main():
    parser = argparse.ArgumentParser(
        description="Start the Digikala Kafka data simulation stream."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Compatibility argument used by the API start command.",
    )
    parser.parse_args()

    stream_data()


if __name__ == "__main__":
    main()
