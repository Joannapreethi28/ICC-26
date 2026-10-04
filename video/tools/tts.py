"""ElevenLabs text-to-speech (key from env ELEVENLABS_API_KEY; never printed).
python video/tools/tts.py VOICE_ID OUT.mp3 "text"
"""
import json
import sys
import urllib.request

from list_voices import key


def tts(voice_id: str, text: str, out: str) -> None:
    body = {"text": text, "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.2, "use_speaker_boost": True}}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
                                 data=json.dumps(body).encode(), headers={"xi-api-key": key(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as f:
        f.write(r.read())


if __name__ == "__main__":
    tts(sys.argv[1], sys.argv[3], sys.argv[2])
    print("wrote", sys.argv[2])
