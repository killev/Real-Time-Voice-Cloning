from pathlib import Path
from encoder import inference as encoder
from vocoder import inference as vocoder
from synthesizer.inference import Synthesizer
import torch
import numpy as np
from encoder.params_model import model_embedding_size as speaker_embedding_size
import librosa


class Generator:
    enc_model_fpath = Path("encoder/saved_models/pretrained.pt")
    voc_model_fpath = Path("vocoder/saved_models/pretrained/pretrained.pt")
    syn_model_dir = Path("synthesizer/saved_models/logs-pretrained/")
    synthesizer = None

    def __init__(self):
        self.synthesizer = Synthesizer(self.syn_model_dir.joinpath("taco_pretrained"), low_mem=False)

    def initialize(self):
        print("Running a test of your configuration...\n")
        if not torch.cuda.is_available():
            print("Your PyTorch installation is not configured to use CUDA. If you have a GPU ready "
                  "for deep learning, ensure that the drivers are properly installed, and that your "
                  "CUDA version matches your PyTorch installation. CPU-only inference is currently "
                  "not supported.")
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

        print("Preparing the encoder, the synthesizer and the vocoder...")
        encoder.load_model(self.enc_model_fpath)

        vocoder.load_model(self.voc_model_fpath)

        ## Run a test
        print("Testing your configuration with small inputs.")
        print("\tTesting the encoder...")
        encoder.embed_utterance(np.zeros(encoder.sampling_rate))

        embed = np.random.rand(speaker_embedding_size)
        embed /= np.linalg.norm(embed)
        embeds = [embed, np.zeros(speaker_embedding_size)]
        texts = ["test 1", "test 2"]
        print("\tTesting the synthesizer... (loading the model will output a lot of text)")
        mels = self.synthesizer.synthesize_spectrograms(texts, embeds)

        mel = np.concatenate(mels, axis=1)
        no_action = lambda *args: None
        print("\tTesting the vocoder...")
        vocoder.infer_waveform(mel, target=200, overlap=50, progress_callback=no_action)
        print("All test passed! You can now synthesize speech.\n\n")

    def generate(self, in_fpath, text, out_fpath):
        try:
            preprocessed_wav = encoder.preprocess_wav(in_fpath)
            original_wav, sampling_rate = librosa.load(in_fpath)
            preprocessed_wav = encoder.preprocess_wav(original_wav, sampling_rate)
            print("Loaded file succesfully")

            embed = encoder.embed_utterance(preprocessed_wav)
            print("Created the embedding")

            texts = [text]
            embeds = [embed]
            # If you know what the attention layer alignments are, you can retrieve them here by
            # passing return_alignments=True
            specs = self.synthesizer.synthesize_spectrograms(texts, embeds)
            spec = specs[0]
            print("Created the mel spectrogram")
            ## Generating the waveform
            print("Synthesizing the waveform:")
            generated_wav = vocoder.infer_waveform(spec)

            generated_wav = np.pad(generated_wav, (0, self..synthesizer.sample_rate), mode="constant")


            librosa.output.write_wav(out_fpath, generated_wav.astype(np.float32),
                                     self.synthesizer.sample_rate)

            print("\nSaved output as %s\n\n" % out_fpath)


        except Exception as e:
            print("Caught exception: %s" % repr(e))
            print("Restarting\n")
