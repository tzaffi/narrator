# Einsteinish Narrates Neil Turok Slides

This is a slight modification of the work done by 
[Charlie Holtz](https://twitter.com/charliebholtz/status/1724815159590293764)
and is a fork of [cbh123/narrator](https://github.com/cbh123/narrator).

## Making Your Own Version

### Get the code and setup python
```sh
git clone https://github.com/tzaffi/narrator
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### AI API's

#### ElevenLabs

If you haven't done so already, sign up for an account at [ElevenLabs](https://elevenlabs.io) and follow [Matthew Berman's "David Attenborough..."](https://www.youtube.com/watch?v=G2VAWXXk1F0&t=3s&ab_channel=MatthewBerman) video for instructions on how to create the narrator's voice.

> Frankly, this was the weakest part of the experiment. Though the narrator sounds convincingly human, I didn't succeed to make him sound much like Einstein. I only trained it on a single sample such as [this one](https://soundcloud.com/blendedprofit/nobel-prize-ceremony-the-war-is-won-but-peace-is-not-the-voice-of-albert-einstein) (but not the same). Perhaps I should have added a few more training clips.


In particular, take note of the
following important ElevenLabs Credentials:
* `ELEVENLABS_API_KEY` - the identifier that is needed for interacting with their API
* `ELEVENLABS_VOICE_ID` - the identifier for the narrator voice which you have generated

After tweaking the narrator's voice to the point that you are satified, you can retrieve
its _voice id_ via the [get voices](https://elevenlabs.io/docs/api-reference/get-voices) endpoint, or by clicking the flask icon next to the voice in the VoiceLab tab.

#### Open API GPT4 Vision Preview
If you haven't done so already, sign up for an account at [OpenAI](https://beta.openai.com/) and fund it with a few dollars so you can call their new Vision API.
You can follow the instructions in the same Berman 
video as above (or dig into the code in [zarrator.py](./zarrator.py))
to gain further understanding.

Take note of:
* `OPENAI_API_KEY=sk-...` - the identifier that is needed for interacting with their API

#### `.env` Secrets File

Once you have all these credentials, you should create a `.env` file that
looks something like:

```env
OPENAI_API_KEY="<the OpenAI API Key>"
ELEVENLABS_API_KEY="<the ElevenLabs API Key>"
ELEVENLABS_VOICE_ID="<the ElevenLabs Narrator Voice ID>"
```

### Seed the Lecture with some Slides
Add some jpeg's to the [slides folder](./slides).
The narration will happen in lexicographic
order of the slide filenames. So I recommend you follow
a predictable naming convention such as:

1. `slide_1.jpg`
2. `slide_2.jpg`
3. `slide_3.jpg`
   
...

### Run it TWICE!

#### The first time you'll generate all the artifacts

On the terminal, run the narrator:

```sh
python narrator.py
```

If all goes well, *for each slide* the following artifacts will be generated in order.
Assuming the slide being narrated is the file `slides/the_slide.jpg`:

1. A base-64 encoding of the image as `slide_encodings/the_slide.b64`
2. **OpenAI**'s narration text for the image as `slide_scripts/the_slide.txt`
3. **ElevenLab**'s audio media for OpenAI's script `slide_audios/the_slide.wav`
4. The narration audio is played through the system's speakers

However, even though step (4) occurs
for each slide in `slides/`, since steps (2) and (3)
take a long time (> 10 secs), the narration audios
have too long of a break in between them to be used
in a final narration. 

Of course, you could just edit the resulting in an audio editor tool and cut out the pauses from
the final narration.

Alternately: play it a second time as explained next.

#### The second time, you'll produce a smooth narration with no pauses in between slide segments

Once again on the terminal, run:

```bash
python narrator.py
```

As all artifacts are _cached_, 
no attempt will be made to generate
the _base-64 encoding_, _slide text_, or _slide audio_
if such artifacts already exists. Consequently,
steps (1), (2), and (3) exit immediately when
the program is run the second time, resulting only
in step (4) taking up any non-neglibible time at all.

Therefore the 2nd (and 3rd, and 4th, ...) time that `narrator.py` is run, it will result
in a smooth audio suitable for recording.

