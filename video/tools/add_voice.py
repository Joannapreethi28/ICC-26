"""Add a shared-library voice to the account: python add_voice.py PUBLIC_OWNER_ID VOICE_ID NAME (key from env; never printed)."""
import json
import sys
import urllib.error
import urllib.request

from list_voices import key

owner, vid, name = sys.argv[1:4]
req = urllib.request.Request(f"https://api.elevenlabs.io/v1/voices/add/{owner}/{vid}", data=json.dumps({"new_name": name}).encode(),
                             headers={"xi-api-key": key(), "Content-Type": "application/json"})
try:
    print(name, "->", json.loads(urllib.request.urlopen(req, timeout=60).read()).get("voice_id"))
except urllib.error.HTTPError as e:
    print(name, "ERROR", e.code, e.read()[:200].decode(errors="ignore"))
