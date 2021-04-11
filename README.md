# NeuralTranslator-cli

## Project details
- Python cli-application that can translate text (English currently) from a number of different formats (plain text, SubRip subtitles) to a few target languages by leveraging powerful [Transformer-based](https://arxiv.org/abs/1706.03762) architectures specialized for translation.
- The app uses the [MarianMT models](https://huggingface.co/transformers/model_doc/marian.html) from the [HuggingFace-Transformers](https://github.com/huggingface/transformers) library.

## Requirements
- Ubuntu Operating system (tested on 20.04)
- NVIDIA GPU - highly recommended

## Instalation
1. Install [Anaconda](https://www.anaconda.com/)
2. Create a new env via: 
    ```
    conda create -n nt python=3.7
    ```
3. Install Pytorch 
    ```
    conda install pytorch torchvision torchaudio cudatoolkit=11.1 -c pytorch -c conda-forge
    ```
4. Install extra pip requiremements: 
    ```
    pip install -r requirements.txt
    ```

## How to run:
- Run `translate.py` with your desired arguments. See below for a detailed description:
    ```
    usage: translate.py [-h] [--input INPUT] [--type {plain,srt,dir}]
                        [--target_language {Romanian,Dutch,German}]
                        [--output OUTPUT]

    optional arguments:
    -h, --help            show this help message and exit
    --input INPUT         Path input file or directory for translation
    --type {plain,srt,dir}
                            The type of input for translation
    --target_language {Romanian,Dutch,German}
                            The language in which we are translating
    --output OUTPUT       Path to output file or directory for translation
    ```