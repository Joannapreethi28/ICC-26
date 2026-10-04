"""List ElevenLabs voices tagged female (key from env ELEVENLABS_API_KEY; never printed)."""
import json
import os
import urllib.request
import winreg


def key() -> str:
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
            k = winreg.QueryValueEx(h, "ELEVENLABS_API_KEY")[0]
    return k


if __name__ == "__main__":
  req = urllib.request.Request("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": key()})
  voices = json.loads(urllib.request.urlopen(req, timeout=30).read())["voices"]
  for v in voices:
    lab = v.get("labels") or {}
    if lab.get("gender") == "female":
        print(f'{v["voice_id"]} | {v["name"]} | {lab.get("accent","")} | {lab.get("age","")} | {lab.get("description", lab.get("descriptive",""))} | {lab.get("use_case","")} | preview: {v.get("preview_url","")}')
