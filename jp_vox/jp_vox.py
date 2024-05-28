import dotenv
import os
import sys
import deepl
import urllib.parse
import requests
import pathlib
import hashlib
import pygame
import argparse

def speak_jp(sentance, source="EN", target="JA"):
    """
    This function gets in a sentance in the language specified by the source variable, 
    then it translates the sentance from the source to the target language.
    Then it sends the text of the translation to voicevox, a japanease text to speech software,
    and gets a soundfile back. Then it plays the soundfile through pygame
    
    """
    dotenv.load_dotenv()

    voicevox_key = os.getenv('VOICEVOX_KEY')
    deepl_key = os.getenv("DEEPL_KEY")

    translator = deepl.Translator(deepl_key)

    result = translator.translate_text(sentance, source_lang=source, target_lang=target).text

    print(result)

    url = "https://deprecatedapis.tts.quest/v2/voicevox"

    settings = urllib.parse.urlencode({
        "text": result,
        "speaker": 13, # male: 13 female: 66, 20, 55, 73
        "emotion": 0,
        "pitch": 0,
        "intonationScale": 1,
        "speedScale": 1,
        "key": voicevox_key
    })

    request = requests.post(f"{url}/audio/?{settings}")
    if request.status_code == 200:

        output_filename = f"voicevox_output_{hashlib.sha256(result.encode()).hexdigest()}.wav"
        output_path = pathlib.Path(output_filename)
        with output_path.open("wb") as f:
            f.write(request.content)

        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(output_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass

        pygame.quit()

        os.remove(output_path)

    else:
        print(f"bad request: {request.status_code}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    
    # command line arguments for target and source language
    parser.add_argument('-target', type=str)
    parser.add_argument('-source', type=str)
    # -text is if you have a text file you want it to play from.
    parser.add_argument('-text', type=str)
    args = parser.parse_args()

    if args.target == None:
        target_lang = "JA"
    else:
        target_lang = args.target
    if args.source == None:
        source_lang = "EN"
    else:
        source_lang = args.source
    if args.text == "y":
        path = input("Path: ")
        with open(path, "r") as f:
            sentance = f.read()
            print(sentance)
        speak_jp(sentance, source=source_lang, target=target_lang)
    else:
        speak_jp(input("Text: "), source=source_lang, target=target_lang)
