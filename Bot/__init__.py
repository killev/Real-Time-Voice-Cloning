from telegram.ext import MessageHandler, Filters
from pathlib import Path
import requests

class Bot:
    chats = {}
    root = None
    generator = None

    def __init__(self, updater, root, generator):
        dispatcher = updater.dispatcher
        self.root = root
        self.generator = generator
        text_handler = MessageHandler(Filters.text, self.handle_message_text)
        audio_handler = MessageHandler(Filters.audio, self.handle_message_audio)
        dispatcher.add_handler(text_handler)
        dispatcher.add_handler(audio_handler)
        print("Bot handler added")

    def chat(self, chat_id, username):
        if not chat_id in self.chats:
            chat_root = self.root.joinpath("Chats/%d-%s" % (chat_id, username))
            self.chats[chat_id] = Chat(root=chat_root, generator=self.generator)
        return self.chats[chat_id]

    def handle_message_text(self, update, context):
        self.chat(update.message.chat_id, update.effective_user.username).handle_message_text(update, context)

    def handle_message_audio(self, update, context):
        self.chat(update.message.chat_id, update.effective_user.username).handle_message_audio(update, context)


class Chat:
    root = None
    generator = None

    def __init__(self, root, generator):
        self.root = root
        self.generator = generator

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

    def result(self):
        count = 0
        for child in self.outcome_dir.iterdir():
            count += 1

        file_name = "out_%i.wav" % count

        return self.outcome_dir.joinpath(file_name)

    def handle_message_text(self, update, context):
        print("Processing text: %d ..." % update.message.chat_id)
        sample_path = self.sample()
        if sample_path is None:
            context.bot.send_message(chat_id=update.message.chat_id, text="No audio sample file provided")
            return
        print(sample_path)
        context.bot.send_message(chat_id=update.message.chat_id, text="Processing... Wait!!!")
        result_path = self.result()

        self.generator.generate_voice(in_fpath=sample_path, text=update.message.text, out_fpath=result_path)
        res = result_path.resolve().open('rb')
        context.bot.send_audio(chat_id=update.message.chat_id, audio=res)

    def handle_message_audio(self, update, context):
        print("Processing audio: %d - %s..." % (update.message.chat_id, update.message.audio))

        file = context.bot.get_file(update.message.audio.file_id)
        sample_path = self.income_dir.joinpath("sample.flac")

        response = requests.get(file.file_path)
        with sample_path.open('wb') as sample:
            sample.write(response.content)


        context.bot.send_message(chat_id=update.message.chat_id, text="Got File")
        context.bot.send_message(chat_id=update.message.chat_id, text="Write a sentence (+-20 words) to be synthesized")

