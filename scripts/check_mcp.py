"""Verify discovery and real trained-model responses on a local or public MCP URL."""
import argparse
import ast
import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def check(url: str) -> None:
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            assert names == {'resolve_sports_query', 'list_supported_intents'}, names
            print('Discovery OK:', ', '.join(sorted(names)))
            for lang in ('en', 'hi', 'ta'):
                reply = await session.call_tool('resolve_sports_query', {
                    'query': 'Who has the most T20I runs?', 'lang': lang})
                assert not reply.isError, reply
                data = reply.structuredContent
                # Gradio 6 may wrap content blocks in a structured `result` envelope.
                if isinstance(data, dict) and 'result' in data and 'language' not in data:
                    data = None
                if data is None:
                    try:
                        data = json.loads(reply.content[0].text)
                    except json.JSONDecodeError:
                        data = ast.literal_eval(reply.content[0].text)
                assert data['language'] == lang and len(data['results']) == 2, data
                assert any(t.startswith('laya:') for t in data['trace']), data['trace']
                assert not any('laya unavailable' in t for t in data['trace'])
                assert all(f['sources'] and f['as_of'] for f in data['results'])
                print(f'{lang}: trained Laya, both records, sources and dates OK')
            reply = await session.call_tool('list_supported_intents', {})
            assert not reply.isError, reply
            print('Catalogue OK')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    asyncio.run(check(parser.parse_args().url))
