from telegram.ext import MessageHandler, Filters
from pathlib import Path
import requests

class Bot:
    chats = {}
    root = None

    def __init__(self, updater, root):
        dispatcher = updater.dispatcher
        self.root = root
        text_handler = MessageHandler(Filters.text, self.handle_message_text)
        audio_handler = MessageHandler(Filters.audio, self.handle_message_audio)
        dispatcher.add_handler(text_handler)
        dispatcher.add_handler(audio_handler)
        print("Bot handler added")

    def chat(self, chat_id, username):
        if not chat_id in self.chats:
            chat_root = self.root.joinpath("Chats/%d-%s" % (chat_id, username))
            self.chats[chat_id] = Chat(root=chat_root)
        return self.chats[chat_id]

    def handle_message_text(self, update, context):
        self.chat(update.message.chat_id, update.effective_user.username).handle_message_text(update, context)

    def handle_message_audio(self, update, context):
        self.chat(update.message.chat_id, update.effective_user.username).handle_message_audio(update, context)


class Chat:
    root = None

    def __init__(self, root):
        self.root = root

    @property
    def income_dir(self):
        res = self.root.joinpath("Incomes/")
        res.mkdir(parents=True, exist_ok=True)
        return res

    @property
    def outcome_dir(self):
        res = self.root.joinpath("Outcomes/")
        res.mkdir(parents=True, exist_ok=True)
        return res

    def sample(self):
        res = None
        for child in self.income_dir.iterdir():
            res = child
        return res

    def handle_message_text(self, update, context):
        print("Processing text: %d ..." % update.message.chat_id)
        if self.sample() is None:
            context.bot.send_message(chat_id=update.message.chat_id, text="No audio sample file provided")
            return
        print(self.sample())
        context.bot.send_message(chat_id=update.message.chat_id, text="Processing... Wait!!!")



    def handle_message_audio(self, update, context):
        print("Processing audio: %d - %s..." % (update.message.chat_id, update.message.audio))

        file = context.bot.get_file(update.message.audio.file_id)
        sample_path = self.income_dir.joinpath("sample.flac")

        response = requests.get(file.file_path)
        with sample_path.open('wb') as sample:
            sample.write(response.content)

        context.bot.send_message(chat_id=update.message.chat_id, text="Got File")
        context.bot.send_message(chat_id=update.message.chat_id, text="Write a sentence (+-20 words) to be synthesized")

