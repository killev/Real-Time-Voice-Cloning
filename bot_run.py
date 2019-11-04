from encoder.params_model import model_embedding_size as speaker_embedding_size

from telegram.ext import Updater
from VoiceGen import Generator
from pathlib import Path
from Bot import Bot
from utils.argutils import print_args
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-u", "--user", type=str,
                        help="Login to messenger")
    parser.add_argument("-p", "--password", type=str,
                        help="password to messenger")

    args = parser.parse_args()
    print_args(args, parser)

    generator = Generator()
    generator.initialize()

    print("Starting bot...\n")

    botRoot = Path("../ChatBotData/")

    client = Bot(args.user, args.password, botRoot, generator)
    client.listen()
