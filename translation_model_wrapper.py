from transformers import MarianTokenizer, MarianMTModel
from typing import List
import torch


class TranslationModelWrapper(object):
    """
    Main NN-based translator model, using pretrained MarianMTModel
    Also handles tokenization, capable of cuda inference
    Main Usage:
        translator = TranslationModelWrapper(src="source language", trg="target language", use_cuda=True/False)
        words: List[str] = translator.translate("This is a phrase I want to translate from <src> to <trg> ")
    """

    def __init__(self, src="en", trg="ro", use_cuda=True):
        self.src = src
        self.trg = trg
        self.use_cuda = use_cuda
        self.mname = f"Helsinki-NLP/opus-mt-{self.src}-{self.trg}"
        with torch.no_grad():
            self.model = MarianMTModel.from_pretrained(self.mname)
            if self.use_cuda:
                self.model = self.model.cuda()
            self.tok = MarianTokenizer.from_pretrained(self.mname)

    def translate(self, texts: List[str]):
        batch = self.tok.prepare_seq2seq_batch(src_texts=texts, return_tensors="pt")

        if self.use_cuda:
            for key in batch.data:
                batch.data[key] = batch.data[key].cuda()

        gen = self.model.generate(**batch)
        words: List[str] = self.tok.batch_decode(gen, skip_special_tokens=True)
        return words