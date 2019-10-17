from encoder.params_model import model_embedding_size as speaker_embedding_size

from telegram.ext import Updater



from pathlib import Path
import sys
from Bot import Bot


if __name__ == '__main__':


    print("Starting telegram bot...\n")

    updater = Updater(token='920553078:AAEvKK2CHxhY1GYxNJ3qa3XzOu0CUq6Bku4', use_context=True)
    botRoot = Path("../ChatBotData/")


    bot = Bot(updater=updater, root=botRoot)



    updater.start_polling()
