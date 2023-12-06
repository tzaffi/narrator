import base64
import os
from os import environ, urandom
from pathlib import Path
import time

from dotenv import load_dotenv
from elevenlabs import generate, play, set_api_key, voices
from openai import OpenAI
import errno

# import json
import simpleaudio as sa

SLIDES_DIR = Path.cwd() / "slides"
ENCODINGS_DIR = Path.cwd() / "slide_encodings"
SCRIPTS_DIR = Path.cwd() / "slide_scripts"
AUDIOS_DIR = Path.cwd() / "slide_audios"

SYSTEM_PROMPT = """
You are Professor Albert Einstein.
Narrate in English the picture of the lecture slide 
as if you are describing the slide to a non-technical audience.
However, do at least read out correctly any formulas or equations on the slide.
Make it snarky and funny. 
Don't repeat yourself. 
Make it super super short. 
Make a big deal about anything super interesting!
"""

USER_PROMPT = "Describe this image"


class Narrator:
    def __init__(self):
        load_dotenv()

        set_api_key(environ.get("ELEVENLABS_API_KEY"))

        # SG_API_KEY = environ.get("SENDGRID_API_KEY")
        # FROM = environ.get("IPING_FROM")
        # TO = environ.get("IPING_TO")

        self.client = OpenAI()

    def encode_image(self, slide):
        """
        Encode an image file into base64 unless it already
        exists, in which case simply return the existing
        base64 encoding.
        """

        encoding_path = ENCODINGS_DIR / f"{slide}.b64"
        try:  # check if encoding already exists
            with open(encoding_path, "r") as encoding_file:
                return encoding_file.read()
        except IOError as e:
            print(f"Encoding not found for {slide=}, generating new encoding")

        image_path = SLIDES_DIR / f"{slide}.jpg"
        with open(image_path, "rb") as image_file:
            encoding = base64.b64encode(image_file.read()).decode("utf-8")
            with open(encoding_path, "w") as encoding_file:
                encoding_file.write(encoding)
            return encoding

    def new_line_prompt(self, base64_image):
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": USER_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            },
        ]

    def analyze_image(self, slide, base64_image, script):
        """
        Send the image to the OpenAI API and return the response for
        continuing the script, unles the slide's script already exists
        in which case simply return the existing script.
        """
        script_path = SCRIPTS_DIR / f"{slide}.txt"
        try:  # check if script already exists
            with open(script_path, "r") as script_file:
                return script_file.read()
        except IOError as e:
            print(f"Script not found for {slide=}, generating new script")

        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
            ]
            + script
            + self.new_line_prompt(base64_image),
            max_tokens=500,
        )
        response_text = slide + ":\n\n" + response.choices[0].message.content
        with open(script_path, "w") as script_file:
            script_file.write(response_text)
        return response_text

    def play_audio(self, slide, text):
        """
        Generate audio from text by calling out to ElevenLabs.io, and play it.
        If the audio file already exists, simply play it.
        """
        audio_path = AUDIOS_DIR / f"{slide}.wav"
        try:  # check if audio already exists
            with open(audio_path, "rb") as audio_file:
                play(audio_file.read())
                return
        except IOError as e:
            print(f"Audio not found for {slide=}, generating new audio")

        audio = generate(text, voice=environ.get("ELEVENLABS_VOICE_ID"))

        with open(audio_path, "wb") as f:
            f.write(audio)

        play(audio)


def main():
    narrator = Narrator()

    script = []

    for file in sorted(SLIDES_DIR.iterdir()):
        slide = str(file).split("/")[-1].split(".")[0]
        if not slide:
            print(f"Skipping special {file=}")
            continue

        print(f"Analyze: {slide=} ({file=})")

        base64_image = narrator.encode_image(slide)
        print(f"{len(base64_image)=:,}")
        analysis = narrator.analyze_image(slide, base64_image, script)

        print("Play audio")
        narrator.play_audio(slide, analysis)
        script.append({"role": "assistant", "content": analysis})


if __name__ == "__main__":
    main()
