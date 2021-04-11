import os
import argparse
from translator import Translator, TranslatorSrt, TranslatorPlainText


def translate_single_file(
    translator: Translator, target_language: str, input: str, output: str
) -> None:
    with open(output, "w") as f:
        f.write(translator.translateFile(open(input), target_language))


def translate_directory(
    input_dir: str, output_dir: str, target_language: str, translation_extension: str
) -> None:
    import glob

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ext = translation_extension
    input_files = glob.glob(os.path.join(input_dir, f"*.{ext}"))
    if len(input_files) > 0:
        translator = (
            TranslatorSrt(targetLanguage=target_language)
            if ext == "srt"
            else TranslatorPlainText(targetLanguage=target_language)
        )
        for input_file in input_files:
            output_file = os.path.join(
                output_dir,
                "".join(os.path.basename(input_file).split(f".{ext}")[:-1])
                + f"_translated_{target_language}.{ext}",
            )
            translate_single_file(
                translator,
                target_language,
                input_file,
                output_file,
            )


def run_translator() -> None:

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", type=str, help="Path input file or directory for translation")
    argparser.add_argument("--type", type=str, choices=["plain", "srt", "dir"], help="The type of input for translation")
    argparser.add_argument(
        "--target_language", type=str, choices=["Romanian", "Dutch", "German"], help="The language in which we are translating"
    )
    argparser.add_argument("--output", type=str, help="Path to output file or directory for translation")
    args = argparser.parse_args()

    input, output, translation_type, target_language = (
        args.input,
        args.output,
        args.type,
        args.target_language,
    )

    error_str = "Make sure your input is a valid file if type is plain or srt, or directory if type is dir!"
    if translation_type == "plain":
        assert os.path.isfile(input), error_str
        translate_single_file(
            TranslatorPlainText(targetLanguage=target_language),
            target_language,
            input,
            output,
        )

    elif translation_type == "srt":
        assert os.path.isfile(input), error_str
        translate_single_file(
            TranslatorSrt(targetLanguage=target_language),
            target_language,
            input,
            output,
        )
    else:  # dir
        # We are going to assume srt files have .srt extension, plain text files have .txt extension
        assert os.path.isdir(input), error_str
        for ext in ["srt", "txt"]:
            translate_directory(input, output, target_language, ext)


if __name__ == "__main__":
    run_translator()