#!/bin/sh
# Probe: can we reach any free, keyless LLM endpoint from the sandbox to run the baseline audit? (3 Oct 2026)
# Result: NO. Pollinations needs a key (its legacy anonymous endpoint returned server errors), DuckDuckGo AI chat sits behind a
# bot-check we must not bypass, OpenRouter needs a key. Claude in Chrome was then tried; it was dropped (see docs/05_decisions_log.md).
curl -s -m 30 https://text.pollinations.ai/models | head -c 3000; echo
curl -s -m 30 -o /dev/null -w "ddg status: %{http_code}\n" https://duckduckgo.com/duckchat/v1/status -H "x-vqd-accept: 1"
curl -s -m 20 -I https://openrouter.ai/api/v1/models | head -3
curl -s -m 120 https://text.pollinations.ai/openai -H 'Content-Type: application/json' \
  -d '{"model":"openai-fast","messages":[{"role":"user","content":"Who has the most T20I runs?"}]}' | head -c 800; echo
