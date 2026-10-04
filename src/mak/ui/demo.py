"""A cricket scorebook interface, with shared REST/MCP resolution."""
from __future__ import annotations
import html
import json
from functools import lru_cache
from urllib.parse import urlsplit
import gradio as gr
from mak import config
from mak.api.service import coverage, health, resolve_sports_query, list_supported_intents
PRESETS = {
    "en": [
        "Who has scored the most career runs in T20 internationals?",
        "women's most T20I runs",
        "men's most ODI wickets",
        "Kohli vs Mandhana T20I runs",
        "Who has the most wickets?",
        "How long is a cricket pitch?",
        "Who has the most T20I maiden overs?",
    ],
    "hi": [
        "T20 इंटरनेशनल में सबसे ज़्यादा रन किसने बनाए?",
        "महिला T20I में सबसे ज़्यादा रन",
        "पुरुष ODI में सबसे ज़्यादा विकेट",
        "कोहली बनाम मंधाना T20I रन",
        "सबसे ज़्यादा विकेट किसने लिए?",
        "क्रिकेट पिच कितनी लंबी होती है?",
        "सबसे ज़्यादा T20I मेडन ओवर किसके हैं?",
    ],
    "ta": [
        "T20 சர்வதேச கிரிக்கெட்டில் அதிக ரன்கள் எடுத்தவர் யார்?",
        "மகளிர் T20I அதிக ரன்கள்",
        "ஆடவர் ODI அதிக விக்கெட்டுகள்",
        "கோலி எதிர் மந்தனா T20I ரன்கள்",
        "அதிக விக்கெட்டுகள் எடுத்தவர் யார்?",
        "கிரிக்கெட் பிச் எவ்வளவு நீளம்?",
        "அதிக T20I மெடன் ஓவர் யாருடையது?",
    ],
}
 
LANG_LABELS = {"en": "English", "hi": "हिन्दी", "ta": "தமிழ்"}
 
CUSTOM_CSS = """
.gradio-container {width:100%!important; min-width:0!important; max-width:1120px!important; margin:auto!important; padding:clamp(14px,3vw,28px)!important; background:#f7f5ed!important; color:#202c27!important}
.gradio-container .contain {width:100%!important; min-width:0!important; padding:0!important}
body {background:#f7f5ed!important}
#masthead {border-top:5px solid #234d3c; padding:20px 0 28px; border-bottom:1px solid #c9cec2; margin-bottom:20px}
.eyebrow {font:600 11px/1.5 Arial,sans-serif; letter-spacing:.16em; text-transform:uppercase; color:#526357; margin:0 0 18px}
#masthead h1 {font:normal clamp(36px,5vw,64px)/1.08 Georgia,serif; letter-spacing:-.04em; margin:0 0 14px; color:#203c2d}
#masthead p {max-width:610px; font-size:16px; line-height:1.6; color:#536056}
.paper-answer {padding:24px 0; min-height:190px; border-top:2px solid #234d3c}
.answer-copy {font-size:17px; line-height:1.8; white-space:pre-line; overflow-wrap:anywhere}
.record-row {display:flex; justify-content:space-between; gap:20px; padding:18px 0; border-bottom:1px solid #d8dbd1}
.record-name {font:24px/1.4 Georgia,serif; margin:4px 0; overflow-wrap:anywhere}
.record-row > div {min-width:0}
.record-number {font:32px/1.2 Georgia,serif; text-align:right; white-space:nowrap}
.result-label {font:600 11px/1.5 Arial,sans-serif; text-transform:uppercase; letter-spacing:.12em; color:#526357; margin-bottom:16px}
.note {font-size:13px; line-height:1.6; color:#536056}
.status {padding:10px 0; border-bottom:1px solid #c9cec2; font-size:12px; color:#536056}
.evidence {border-left:2px solid #c9cec2; padding:0 0 0 18px; margin:18px 0}
.evidence blockquote {margin:12px 0; font:20px/1.6 Georgia,serif; color:#394b40}
.table-wrap {overflow:auto; width:100%}
table.sources {border-collapse:collapse; width:100%; font-size:13px; text-align:left}
.sources th,.sources td {padding:12px 10px; border-bottom:1px solid #d8dbd1; vertical-align:top}
.sources th {font-weight:600; color:#526357}
.sources a {color:#23533c; text-decoration:underline; text-underline-offset:3px}
.trace {white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.8 monospace}
#ask-button {border-radius:3px!important; background:#234d3c!important; color:#fff!important}
#language-picker label {background:#efeee5!important; color:#202c27!important; border:1px solid #c9cec2!important}
#language-picker label.selected {background:#e0eadf!important; border-color:#234d3c!important}
footer {display:none!important}
@media(max-width:600px) {.gradio-container {padding:18px 14px!important} #masthead {padding-bottom:18px} .paper-answer {min-height:100px}}
"""
THEME = gr.themes.Base(primary_hue='green', neutral_hue='stone',
                       font=['Arial', 'sans-serif'], radius_size='sm').set(
    body_background_fill='#f7f5ed', body_background_fill_dark='#f7f5ed',
    body_text_color='#202c27', body_text_color_dark='#202c27',
    block_background_fill='#f7f5ed', block_background_fill_dark='#f7f5ed',
    background_fill_primary='#fffef9', background_fill_primary_dark='#fffef9',
    background_fill_secondary='#efeee5', background_fill_secondary_dark='#efeee5',
    input_background_fill='#fffef9', input_background_fill_dark='#fffef9',
    block_label_text_color='#536056', block_label_text_color_dark='#536056',
    block_title_text_color='#202c27', block_title_text_color_dark='#202c27',
    body_text_color_subdued='#536056', body_text_color_subdued_dark='#536056',
    border_color_primary='#c9cec2', border_color_primary_dark='#c9cec2',
    block_shadow='none', block_border_width='0px')


def _esc(value) -> str:
    return html.escape(str(value), quote=True)


@lru_cache(maxsize=1)
def _captures() -> list[dict]:
    path = config.ROOT / 'results/e1/raw/plain.jsonl'
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def baseline_html(query: str, lang: str) -> str:
    capture = next((r for r in _captures() if r.get('user', '').strip() == query.strip()
                    and r.get('language') == lang and r.get('seed') == 42), None)
    if not capture:
        return '<p class="note">No saved plain-model answer for this exact question. This panel never invents a comparison.</p>'
    date = capture.get('raw_response', {}).get('created_at', 'Date unavailable')
    return (f'<div class="evidence"><p class="result-label">Saved plain-model answer</p>'
            f'<blockquote>{_esc(capture.get("answer", ""))}</blockquote>'
            f'<p class="note">{_esc(capture.get("model", ""))} · {_esc(date)}<br>'
            'Recorded local-model output; may be incorrect. One example, not a bias rate.</p></div>')


def _sources(result: dict) -> str:
    rows = []
    for f in result['results']:
        links = []
        for i, url in enumerate(f['sources'], 1):
            if urlsplit(url).scheme in ('http', 'https'):
                links.append(f'<a href="{_esc(url)}" target="_blank" rel="noopener noreferrer">Source {i}</a>')
        rows.append('<tr>' + ''.join(f'<td>{_esc(v)}</td>' for v in
                    (f['gender'], f['holder_local'] or f['holder'], f['format'],
                     f['value'] + ' ' + f['unit'], f['as_of'], f['trust']))
                    + '<td>' + ' · '.join(links) + '</td></tr>')
    if not rows:
        return '<p class="note">No record retrieved. No number has been supplied.</p>'
    headings = ['Category', 'Holder', 'Format', 'Record', 'As of', 'Evidence', 'Sources']
    return '<div class="table-wrap"><table class="sources"><thead><tr>' + ''.join(
        f'<th scope="col">{h}</th>' for h in headings) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'


def resolve_fn(query: str, lang: str) -> tuple[str, str, str, str]:
    if not query or not query.strip() or len(query) > 2000:
        return ('<p class="note">Enter a question between 1 and 2,000 characters.</p>', '', '', '')
    r = resolve_sports_query(query, lang)
    message = r['answer_text']
    if not message:
        message = ('This question does not need a gender-aware record lookup.'
                   if r['decision'] == 'no_intervention' else 'No verified answer is available for this question.')
    status = 'Rules-only result' if any('rules-only' in t for t in r['trace']) else 'See decision trace for classifier details'
    answer = (f'<div class="paper-answer" role="status" lang="{_esc(r["language"])}">'
              f'<p class="result-label">Make AI Know Her · {_esc(r["decision"].replace("_", " "))}</p>'
              f'<div class="answer-copy">{_esc(message)}</div>'
              f'<p class="note">{status} · {r["latency_ms"]:.0f} ms for this request</p></div>')
    if r['results']:
        categories = {'en': {'women': 'Women', 'men': 'Men'},
                      'hi': {'women': 'महिला', 'men': 'पुरुष'},
                      'ta': {'women': 'மகளிர்', 'men': 'ஆடவர்'}}
        rows = []
        for fact in r['results']:
            rows.append(f'<div class="record-row"><div><div class="result-label">'
                        f'{categories[r["language"]][fact["gender"]]} · {_esc(fact["format"])}</div>'
                        f'<div class="record-name">{_esc(fact["holder_local"] or fact["holder"])}</div>'
                        f'<div class="note">{_esc(fact["country"] or "")} · {_esc(fact["as_of"])}</div></div>'
                        f'<div><div class="record-number">{_esc(fact["value"])}</div>'
                        f'<div class="note">{_esc(fact["unit"])}</div></div></div>')
        answer = (f'<div class="paper-answer" role="status" lang="{_esc(r["language"])}">'
                  '<p class="result-label">Make AI Know Her · The records</p>' + ''.join(rows)
                  + f'<p class="note">Dated snapshots · {status} · {r["latency_ms"]:.0f} ms</p>'
                  + '<details><summary>Full answer</summary><div class="answer-copy">'
                  + _esc(message) + '</div></details></div>')
    trace = '<div class="trace">' + _esc('\n'.join(r['trace'])) + '</div>'
    return answer, trace, _sources(r), baseline_html(query, r['language'])


def update_presets(lang: str):
    return gr.Dropdown(choices=PRESETS[lang], value=PRESETS[lang][0]), PRESETS[lang][0]


def build_demo() -> gr.Blocks:
    """Build the demo and register exactly two public MCP tools."""
    c = coverage()
    model = health()['model_status']
    with gr.Blocks(title='Make AI Know Her', analytics_enabled=False) as demo:
        gr.HTML('<header id="masthead"><div class="eyebrow">A fairer view of cricket</div>'
                '<h1>Whose record are we missing?</h1>'
                '<p>Ask a cricket question. See women’s and men’s records together, with the sources and dates behind every answer.</p></header>')
        gr.HTML(f'<div class="status">Make AI Know Her · EN / हिन्दी / தமிழ் · Model: {_esc(model.replace("_", " "))}'
                + (' — this machine will use rules only until trained weights are available.' if model == 'missing_weights' else '') + '</div>')
        with gr.Row(equal_height=False):
            with gr.Column(scale=4, min_width=280):
                lang = gr.Radio(choices=[('English', 'en'), ('हिन्दी', 'hi'), ('தமிழ்', 'ta')], value='en', label='Answer language', elem_id='language-picker')
                preset = gr.Dropdown(choices=PRESETS['en'], value=PRESETS['en'][0], label='Try a question')
                query = gr.Textbox(value=PRESETS['en'][0], label='Your question', lines=3, max_lines=5)
                submit = gr.Button('Show the records', variant='primary', elem_id='ask-button')
                gr.HTML('<p class="note">A neutral question shows both categories. Ask explicitly for women or men to focus the answer.</p>')
            with gr.Column(scale=6, min_width=280):
                answer = gr.HTML('<div class="paper-answer"><p class="result-label">The answer</p><p class="answer-copy">A complete record starts with a complete question.</p><p class="note">Choose a question, then show the records.</p></div>')
                before = gr.HTML('')
        with gr.Accordion('Sources & snapshot dates', open=True):
            sources = gr.HTML('<p class="note">Sources appear with your answer. Records are dated snapshots, not live scores.</p>')
        with gr.Accordion('How this answer was selected', open=False):
            trace = gr.HTML('<p class="note">The policy and classifier trace will appear here.</p>')
        with gr.Accordion('What this demo covers', open=False):
            gr.HTML(f'<p class="note">{c["golden_records"]} stored records across {c["golden_intents"]} intents. '
                    f'{c["supported_intents"]} intents in the catalogue; catalogue support does not mean data is available.<br>'
                    f'Computed database: {"available" if c["computed_database_available"] else "not present on this machine"}. '
                    'English, Hindi and Tamil. Each retrieved row carries its own snapshot date.<br>'
                    'Missing records are left unanswered. A model selects categories; it never writes record values.</p>')
        outputs = [answer, trace, sources, before]
        lang.change(update_presets, lang, [preset, query], api_visibility='private', queue=False)
        preset.change(lambda value: value, preset, query, api_visibility='private', queue=False)
        for event in (submit.click, query.submit):
            event(resolve_fn, [query, lang], outputs, api_visibility='private', concurrency_limit=1, concurrency_id='resolve')
        gr.api(resolve_sports_query, api_name='resolve_sports_query', concurrency_limit=1, concurrency_id='resolve')
        gr.api(list_supported_intents, api_name='list_supported_intents', queue=False)
    return demo.queue(max_size=16, default_concurrency_limit=1)


create_demo = build_demo

if __name__ == '__main__':
    build_demo().launch(server_name='127.0.0.1', server_port=7860, mcp_server=True,
                        theme=THEME, css=CUSTOM_CSS, show_error=False)

