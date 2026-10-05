# Live MCP test — 4 October 2026
## Current live test

- Demo: https://ea95ffb3e669617b62.gradio.live
- MCP: https://ea95ffb3e669617b62.gradio.live/gradio_api/mcp/
- Restarted 5 October at Sir Jabin's request. Public MCP discovery confirms the new conversational-answer guidance. Trained EN/HI/TA calls and catalogue pass. Client connections must use this new URL; this session has no connected browser to refresh their metadata.
- Efanio confirmed Sir Jabin's approval in chat before launch, including the standard tunnel-helper download.
- Verified over the public HTTPS URL: MCP initialization, exact two-tool discovery, EN/HI/TA calls with real Laya traces and sourced/dated records, and catalogue call.
- Server process: PID 37220 on this launch, localhost port 7862. Stop this specific process to end the tunnel; PID may change on restart. Logs: results/demo_reload_stdout.log and results/demo_reload_stderr.log. Do not commit machine logs.
- Gradio reports up to one week, best effort. The endpoint stops when the laptop sleeps, disconnects or the process exits. Restarting sharing may change the URL.
- Consumer-app connection has not yet been verified inside ChatGPT or Gemini accounts; the public MCP transport and trained inference have been verified independently.

## Prepared route

Use a temporary Gradio HTTPS share tunnel to this laptop for today's ChatGPT/Gemini test. No Hugging Face account or hosted Space is needed. The model remains local. This is temporary access, not durable hosting: the laptop and Python process must stay running.

The launcher fails if trained Laya cannot load or its EN/HI/TA smoke checks fail. It does not download model files. The share option may download Gradio's standard FRP tunnel helper from its official CDN; the installed Gradio package checks the helper's SHA-256.

**Approval gate:** `document/efanio_split.md` requires Sir Jabin's OK before public deployment and model/package downloads. Obtain approval for this temporary public endpoint and the tunnel helper before using `--share`.

```powershell
python scripts/serve_demo.py             # local-only port 7862; warms real Laya
python scripts/check_mcp.py http://127.0.0.1:7862/gradio_api/mcp/

# Only after public-test approval:
python scripts/serve_demo.py --share
# Copy the printed MCP_URL, then verify it:
python scripts/check_mcp.py https://YOUR-HOST.gradio.live/gradio_api/mcp/
```

If the local-only server still occupies 7862, stop that process first or add `--port 7863` to the shared launcher. No authentication is configured for this read-only test: anyone with the public URL can query records and use laptop inference capacity. Model files, repository Git metadata and private research directories are blocked from Gradio file serving. Do not broaden allowed_paths. The queue allows 16 pending jobs with one inference at a time.

## ChatGPT

Follow the account's developer-mode connection flow (labels vary across rollouts): enable Developer mode, add a custom app/plugin using the printed HTTPS MCP URL, select No authentication if requested, then enable that connection in a new chat.

Official instructions: https://developers.openai.com/plugins/deploy/connect-chatgpt
Gradio-specific example: https://gradio.app/guides/building-chatgpt-apps-with-gradio

## Gemini (US personal account)

Google's current dedicated guide lists: age 18+, US, personal Google account, Keep Activity on, English custom-app interface. In Gemini web, open Settings / Connected Apps, add a custom app with the MCP URL, and follow the connection flow. Some accounts may route via Personal Intelligence. If the option is absent or authentication is demanded, record the exact UI rather than treating a US account alone as proof of access.

Official instructions: https://support.google.com/gemini/answer/17209137?hl=en

## Test prompts and evidence

1. Use Make AI Know Her to answer: Who has the most T20I runs? Include both categories, source links and each record's as-of date.
2. Use Make AI Know Her for women's most T20I runs.
3. Use Make AI Know Her for men's most ODI wickets.
4. Use Make AI Know Her to answer the first question in Hindi, then Tamil (lang=hi / lang=ta).
5. Ask for a named player's data that is absent locally; check it does not substitute a global leader.

Inspect the actual tool call: resolve_sports_query must run and the returned trace must contain `laya:` rather than `laya unavailable`. A plausible answer alone does not prove the app called MCP. Save app, model label, date, account region, tool invocation and screenshot; these are connected-tool demonstrations, not E5 unassisted baseline observations.

The external assistant can rephrase the result; it is not replaced by Laya. Laya classifies the question locally, fixed code applies policy, and database rows supply facts.
