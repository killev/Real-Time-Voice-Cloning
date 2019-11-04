from telegram.ext import MessageHandler, Filters
import requests
from fbchat import Client
from fbchat.models import *


def print_iterator(it):
    for x in it:
        print(x, end=' ')
    print('')  # for new line


class Bot(Client):
    chats = {}
    root = None
    generator = None

    def __init__(self, login, password, root, generator):
        self.root = root
        self.generator = generator
        super(Bot, self).__init__(login, password)
        print("Bot initialized")

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        if author_id == self.uid:
            return

        if message_object.attachments:
            self.handle_message_audio(author_id, message_object, message_object.attachments[0], thread_id, thread_type)
            return

        print("Text message will be handled here...")
        self.handle_message_text(author_id, message_object, thread_id, thread_type)

    def chat(self, chat_id, username):
        if not chat_id in self.chats:
            chat_root = self.root.joinpath("Chats/%s-%s" % (chat_id, username))
            self.chats[chat_id] = Chat(root=chat_root, generator=self.generator)
        return self.chats[chat_id]

    def handle_message_text(self, author_id, message, thread_id, thread_type):
        info = self.fetchUserInfo(author_id)
        self.chat(thread_id, info[author_id].name)\
            .handle_message_text(message,
                                 lambda message1: self.send(message1, thread_id, thread_type),
                                 lambda file: self.sendLocalFiles([file], "Converted audio", thread_id, thread_type))

    def handle_message_audio(self, author_id, message, attachment, thread_id, thread_type):
        info = self.fetchUserInfo(author_id)
        print(info[author_id].name)
        self.chat(thread_id, info[author_id].name)\
            .handle_message_audio(message, attachment, lambda message1: self.send(message1, thread_id, thread_type))


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

    def handle_message_text(self, message, send, send_file):
        print("Processing text: %s ..." % message.text)
        sample_path = self.sample()
        if sample_path is None:
            send(Message(text="No sample uploaded... Send and audio to me"))
            return
        print(sample_path)
        send(Message(text="Processing... Wait!!!"))
        result_path = self.result()

        self.generator.generate_voice(in_fpath=sample_path, text=message.text, out_fpath=result_path)
        send(Message(text="Done... Take a file!!!"))
        print(str(result_path))
        send_file(str(result_path))

    def handle_message_audio(self, message, attachment, send):

        send(Message(
            text="Downloading your sample..."
        ))

        sample_path = self.income_dir.joinpath("sample.flac")

        response = requests.get(attachment.url)
        with sample_path.open('wb') as sample:
            sample.write(response.content)

        send(Message(
            text="Done!"
        ))
        send(Message(
            text="Write a sentence (+-20 words) to be synthesized"
        ))

