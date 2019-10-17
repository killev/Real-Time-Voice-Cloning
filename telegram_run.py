from encoder.params_model import model_embedding_size as speaker_embedding_size

from telegram.ext import Updater
from VoiceGen import Generator
from pathlib import Path
from Bot import Bot


if __name__ == '__main__':

    generator = Generator()
    generator.initialize()

    print("Starting telegram bot...\n")

    updater = Updater(token='920553078:AAEvKK2CHxhY1GYxNJ3qa3XzOu0CUq6Bku4', use_context=True)
    botRoot = Path("../ChatBotData/")

    bot = Bot(updater=updater, root=botRoot, generator=generator)

    updater.start_polling()
