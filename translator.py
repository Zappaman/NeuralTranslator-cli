"""
Generically handles parsing logic of input files
"""
from typing import TextIO, List, Union, Text
from translation_model_wrapper import TranslationModelWrapper
from tqdm import tqdm
import re


class TrBlock(object):
    """
    Translation block class
        - text: Text to be shown on screen
        - pre_text: Meta information placed before text
        - post_text: Meta information placed after text
    """

    def __init__(self, text: str = None, pre_text: str = None, post_text: str = None):
        self.text = text
        self.pre_text = pre_text
        self.post_text = post_text


class TrBlockList(object):
    """
    Translation block list class
        - trBlockList: List of Translation Blocks
        - meta: meta-information to be put at start of file
    """

    def __init__(self, trBlockList, meta):
        self.meta = meta
        self.trBlockList = trBlockList


class Translator(object):
    """
    Generic parser abstract class
        - input2TrBlockList(input: TextIO) -> List[TrBlock]
        - trBlockList2File(trBlockList: List[TrBlock], fileName: str, batchSize) -> None
    """

    def __init__(self):
        self.targetLanguage = None
        self.translationModelWrapper = None

    @staticmethod
    def _decodeTargetLanguage(lan):
        if lan == "Romanian":
            return "ro"
        elif lan == "Dutch":
            return "nl"
        elif lan == "German":
            return "de"
        else:
            assert False, f"Target Language {lan} not supported"

    def input2TrBlockList(self, input: Union[TextIO, Text]) -> List[TrBlock]:
        raise NotImplementedError()

    def trBlockList2File(
        self, trBlockList: TrBlockList, translateCbk=None, batchSize=120
    ) -> str:
        ret_str: str = ""
        blocks = trBlockList.trBlockList
        meta = trBlockList.meta
        ret_str += meta + "\n"

        preTextList = []
        toTranslateList = []

        for block in tqdm(blocks):
            text = block.text.strip()
            toTranslateList += [text]
            preTextList += [block.pre_text.strip()]

            if len(toTranslateList) == batchSize:  # translate current batch
                translatedList = translateCbk(toTranslateList)
                for pre_text, translated_text in zip(preTextList, translatedList):
                    ret_str += pre_text + "\n" + translated_text + "\n\n"

                # reset translation list
                toTranslateList = []
                preTextList = []

        if len(toTranslateList) > 0:  # deal with any remaining extra blocks
            translatedList = translateCbk(toTranslateList)
            for pre_text, translated_text in zip(preTextList, translatedList):
                ret_str += pre_text + "\n" + translated_text + "\n\n"

        return ret_str

    def translateFile(
        self, file: Union[TextIO, Text], targetLanguage="Romanian", batchSize=120
    ) -> None:
        if targetLanguage != self.targetLanguage:
            print(
                "Queued target language is different from current translator language, switching translator..."
            )
            self.translationModelWrapper = TranslationModelWrapper(
                trg=Translator._decodeTargetLanguage(targetLanguage)
            )
            self.targetLanguage = targetLanguage
        return self.trBlockList2File(
            self.input2TrBlockList(file),
            translateCbk=self.translationModelWrapper.translate,
            batchSize=batchSize,
        )


class TranslatorPlainText(Translator):
    def __init__(self, targetLanguage="Romanian"):
        super().__init__()

        self.translationModelWrapper = TranslationModelWrapper(
            trg=Translator._decodeTargetLanguage(targetLanguage)
        )
        self.targetLanguage = targetLanguage

        # Regex that delimits the blocks of text that get translated at once
        self.delim_regex = re.compile(
            r"(?P<pre>[\n\.\-\!\?]*)([^\n\-\.\!\?]+)(?P<post>[\n\.\-\!\?]*)"
        )

    def input2TrBlockList(self, input: Union[TextIO, Text]) -> TrBlockList:
        file_str = input.read() if type(input) != type("generic string") else input

        if type(file_str).__name__ != type("generic string").__name__:
            file_str = file_str.decode("utf-8")  # .replace("\r\n", "\n")

        file_str.replace("\r\n", "\n")

        trBlockList = TrBlockList(
            [
                TrBlock(block[1], block[0], block[2])
                for block in self.delim_regex.findall(file_str)
            ],
            "",  # empty meta
        )

        return trBlockList


class TranslatorSrt(Translator):
    """
    Srt file parser class, implements Translator interface
    """

    def __init__(self, targetLanguage="Romanian"):
        super().__init__()

        self.translationModelWrapper = TranslationModelWrapper(
            trg=Translator._decodeTargetLanguage(targetLanguage)
        )
        self.targetLanguage = targetLanguage

        # Regex that delimits the blocks of text that get translated at once
        self.delim_regex = re.compile(
            r"((\d+)[\r\n](((\d+[:]*)+,\d+) --> ((\d+[:]*)+,\d+))\n)"
        )
        # n % block_idx:
        #   0 -> text
        #   1 -> full match
        self.block_idx = 8

    def input2TrBlockList(self, input: TextIO) -> TrBlockList:
        file_str = input.read()

        if type(file_str).__name__ != type("generic string").__name__:
            file_str = file_str.decode("utf-8")  # .replace("\r\n", "\n")

        file_str.replace("\r\n", "\n")

        blocks = self.delim_regex.split(file_str)
        texts, pre_texts = [], []
        meta = blocks[0]
        for idx, _ in enumerate(blocks):
            if idx % self.block_idx == 0 and idx != 0:
                texts.append(blocks[idx])
            elif idx % self.block_idx == 1:
                pre_texts.append(blocks[idx])

        trBlocks = [TrBlock(text, pre_text) for text, pre_text in zip(texts, pre_texts)]
        trBlockList = TrBlockList(trBlocks, meta)
        return trBlockList