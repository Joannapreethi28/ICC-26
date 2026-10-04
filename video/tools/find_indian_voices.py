"""Search the ElevenLabs shared voice library for female Indian-accent English voices (key from env; never printed)."""
import json
import urllib.parse
import urllib.request

from list_voices import key

q = urllib.parse.urlencode({"gender": "female", "accent": "indian", "language": "en", "page_size": 30, "sort": "usage_character_count_1y"})
req = urllib.request.Request(f"https://api.elevenlabs.io/v1/shared-voices?{q}", headers={"xi-api-key": key()})
data = json.loads(urllib.request.urlopen(req, timeout=30).read())
for v in data.get("voices", []):
    print(f'{v["voice_id"]} | owner {v["public_owner_id"]} | {v["name"]} | {v.get("accent")} | {v.get("age")} | {v.get("use_case")} | {v.get("descriptive")} | uses {v.get("cloned_by_count")} | free_users_allowed {v.get("free_users_allowed")} | {(v.get("description") or "")[:90]}')
