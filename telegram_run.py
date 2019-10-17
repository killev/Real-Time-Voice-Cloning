from encoder.params_model import model_embedding_size as speaker_embedding_size
import torch
from telegram.ext import Updater

from encoder import inference as encoder
from vocoder import inference as vocoder
from synthesizer.inference import Synthesizer
import numpy as np
from pathlib import Path
import sys
from Bot import Bot


def echo(update, context):
    print("Received telegram message")
    context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


if __name__ == '__main__':




    print("Running a test of your configuration...\n")
    if not torch.cuda.is_available():
        print("Your PyTorch installation is not configured to use CUDA. If you have a GPU ready "
              "for deep learning, ensure that the drivers are properly installed, and that your "
              "CUDA version matches your PyTorch installation. CPU-only inference is currently "
              "not supported.", file=sys.stderr)
        quit(-1)
    print("PyTorch is available and working...")
    device_id = torch.cuda.current_device()
    gpu_properties = torch.cuda.get_device_properties(device_id)
    print("Found %d GPUs available. Using GPU %d (%s) of compute capability %d.%d with "
          "%.1fGb total memory.\n" %
          (torch.cuda.device_count(),
           device_id,
           gpu_properties.name,
           gpu_properties.major,
           gpu_properties.minor,
           gpu_properties.total_memory / 1e9))
    ## Load the models one by one.
    enc_model_fpath = Path("encoder/saved_models/pretrained.pt")
    voc_model_fpath = Path("vocoder/saved_models/pretrained/pretrained.pt")
    syn_model_dir = Path("synthesizer/saved_models/logs-pretrained/")

    print("Preparing the encoder, the synthesizer and the vocoder...")
    encoder.load_model(enc_model_fpath)
    synthesizer = Synthesizer(syn_model_dir.joinpath("taco_pretrained"), low_mem=False)
    vocoder.load_model(voc_model_fpath)

    ## Run a test
    print("Testing your configuration with small inputs.")
    # Forward an audio waveform of zeroes that lasts 1 second. Notice how we can get the encoder's
    # sampling rate, which may differ.
    # If you're unfamiliar with digital audio, know that it is encoded as an array of floats
    # (or sometimes integers, but mostly floats in this projects) ranging from -1 to 1.
    # The sampling rate is the number of values (samples) recorded per second, it is set to
    # 16000 for the encoder. Creating an array of length <sampling_rate> will always correspond
    # to an audio of 1 second.
    print("\tTesting the encoder...")
    encoder.embed_utterance(np.zeros(encoder.sampling_rate))

    # Create a dummy embedding. You would normally use the embedding that encoder.embed_utterance
    # returns, but here we're going to make one ourselves just for the sake of showing that it's
    # possible.
    embed = np.random.rand(speaker_embedding_size)
    # Embeddings are L2-normalized (this isn't important here, but if you want to make your own
    # embeddings it will be).
    embed /= np.linalg.norm(embed)
    # The synthesizer can handle multiple inputs with batching. Let's create another embedding to
    # illustrate that
    embeds = [embed, np.zeros(speaker_embedding_size)]
    texts = ["test 1", "test 2"]
    print("\tTesting the synthesizer... (loading the model will output a lot of text)")
    mels = synthesizer.synthesize_spectrograms(texts, embeds)

    # The vocoder synthesizes one waveform at a time, but it's more efficient for long ones. We
    # can concatenate the mel spectrograms to a single one.
    mel = np.concatenate(mels, axis=1)
    # The vocoder can take a callback function to display the generation. More on that later. For
    # now we'll simply hide it like this:
    no_action = lambda *args: None
    print("\tTesting the vocoder...")
    # For the sake of making this test short, we'll pass a short target length. The target length
    # is the length of the wav segments that are processed in parallel. E.g. for audio sampled
    # at 16000 Hertz, a target length of 8000 means that the target audio will be cut in chunks of
    # 0.5 seconds which will all be generated together. The parameters here are absurdly short, and
    # that has a detrimental effect on the quality of the audio. The default parameters are
    # recommended in general.
    vocoder.infer_waveform(mel, target=200, overlap=50, progress_callback=no_action)

    print("All test passed! You can now synthesize speech.\n\n")
    print("Starting telegram bot...\n")

    updater = Updater(token='920553078:AAEvKK2CHxhY1GYxNJ3qa3XzOu0CUq6Bku4', use_context=True)
    botRoot = Path("../ChatBotData/")


    bot = Bot(updater=updater, root=botRoot)



    updater.start_polling()
