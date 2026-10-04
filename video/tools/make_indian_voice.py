"""Free Indian-English narration; isolated edge-tts dependency, no API key."""
import asyncio
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'test-results/demo-tools/edge-packages'))
import edge_tts

OUT = ROOT / 'video/voice-indian'
VOICE = 'en-IN-NeerjaNeural'

def timestamp(seconds):
    ms = round(seconds * 1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def captions(words):
    groups, group = [], []
    for word in words:
        group.append(word)
        if len(' '.join(w['text'] for w in group)) >= 48 or re.search(r'[.!?;]$', word['text']):
            groups.append(group)
            group = []
    if group:
        groups.append(group)
    return '\n'.join(f"{i}\n{timestamp(g[0]['offset']/1e7)} --> {timestamp((g[-1]['offset']+g[-1]['duration'])/1e7)}\n{' '.join(w['text'] for w in g)}\n" for i,g in enumerate(groups,1))

async def main():
    OUT.mkdir(exist_ok=True)
    voices = await edge_tts.list_voices()
    selected = next(v for v in voices if v['ShortName'] == VOICE)
    assert selected['Gender'] == 'Female' and selected['Locale'] == 'en-IN'
    blocks = []
    for block in re.split(r'\n\s*\n', (ROOT/'video/narration.txt').read_text(encoding='utf-8').strip()):
        number, text = block.split('\n',1)
        blocks.append((number.strip(), text.strip()))
    blocks.append(('06-fallback', 'Gemini is not connected to our tool in this recording. Here is the same question in our own demo, showing the category decision and sourced records directly.'))
    manifest = []
    for number, text in blocks:
        audio, alignment = OUT/f'{number}.mp3', OUT/f'{number}.json'
        if audio.exists() and alignment.exists():
            words = json.loads(alignment.read_text())
        else:
            words = []
            with audio.open('wb') as f:
                async for chunk in edge_tts.Communicate(text, VOICE, rate='-5%', boundary='WordBoundary').stream():
                    if chunk['type'] == 'audio':
                        f.write(chunk['data'])
                    elif chunk['type'] == 'WordBoundary':
                        words.append(chunk)
            assert words and audio.stat().st_size > 1000
            alignment.write_text(json.dumps(words, indent=2), encoding='utf-8')
        (OUT/f'{number}.srt').write_text(captions(words), encoding='utf-8')
        (OUT/f'{number}.txt').write_text(text+'\n', encoding='utf-8')
        end = (words[-1]['offset']+words[-1]['duration'])/1e7
        manifest.append({'scene':number, 'speech_end_seconds':end, 'bytes':audio.stat().st_size})
        print(f'{number}: {end:.2f}s, audio + captions ready', flush=True)
    (OUT/'manifest.json').write_text(json.dumps({'voice':selected,'rate':'-5%','scenes':manifest},indent=2),encoding='utf-8')
    print('Main speech duration:',round(sum(s['speech_end_seconds'] for s in manifest if s['scene']!='06-fallback'),2))

if __name__ == '__main__':
    asyncio.run(main())
