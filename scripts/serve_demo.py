"""Warm the trained model before starting a local or explicitly shared MCP demo.

Local: python scripts/serve_demo.py
After Sir Jabin's public-test approval: python scripts/serve_demo.py --share
The share option downloads Gradio's checksum-verified tunnel helper if absent.
"""
from __future__ import annotations

import argparse
import os


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--share', action='store_true', help='Create a temporary public HTTPS URL; requires team approval')
    parser.add_argument('--port', type=int, default=7862)
    args = parser.parse_args()

    # Model files are already provisioned. Startup must not fetch missing artifacts.
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['GRADIO_ANALYTICS_ENABLED'] = 'False'
    os.environ.pop('GRADIO_VIBE_MODE', None)
    os.environ.pop('GRADIO_ALLOWED_PATHS', None)

    from mak import config
    from mak.api.service import health, resolve_sports_query
    from mak.nlu.laya_head import LayaHead
    print('Loading trained Laya locally; no model downloads...', flush=True)
    LayaHead.load()  # Deliberately fail startup instead of publicly demonstrating rules-only.
    for language in ('en', 'hi', 'ta'):
        result = resolve_sports_query('Who has the most T20I runs?', language)
        if (any('laya unavailable' in step for step in result['trace'])
                or result['fallback'] == 'error' or len(result['results']) != 2):
            raise RuntimeError(f'Trained-model startup check failed for {language}')
        print(f'Ready: {language}, {result["decision"]}, {result["latency_ms"]:.0f} ms', flush=True)
    print(f'Model status: {health()["model_status"]}', flush=True)

    from mak.ui.demo import build_demo, THEME, CUSTOM_CSS
    demo = build_demo()
    _, local_url, share_url = demo.launch(
        server_name='127.0.0.1', server_port=args.port, share=args.share,
        mcp_server=True, theme=THEME, css=CUSTOM_CSS,
        show_error=False, prevent_thread_lock=True, max_threads=8,
        favicon_path=str(config.ROOT / 'logo' / 'favicon.png'),
        allowed_paths=[], blocked_paths=[str(config.ROOT / 'models'),
                                        str(config.ROOT / '.git'),
                                        str(config.ROOT / 'icc-make-ai-know-her/source_docs')],
    )
    # MCP clients that read server icons (MCP 2025-11-25 Implementation.icons) show our logo; ChatGPT uses its connector form icon.
    import base64
    from mcp.types import Icon
    logo = base64.b64encode((config.ROOT / 'logo' / 'logo_mcp_128.png').read_bytes()).decode()
    demo.mcp_server_obj.mcp_server.icons = [Icon(src=f'data:image/png;base64,{logo}', mimeType='image/png', sizes=['128x128'])]
    demo.mcp_server_obj.mcp_server.website_url = 'https://github.com/Joannapreethi28/ICC-26'
    if args.share and not share_url:
        demo.close()
        raise RuntimeError('Public tunnel failed; no public endpoint is ready')
    url = share_url or local_url
    print(f'DEMO_URL={url}', flush=True)
    print(f'MCP_URL={url.rstrip("/")}/gradio_api/mcp/', flush=True)
    print('Keep this process and laptop running. Ctrl+C stops access.', flush=True)
    demo.block_thread()


if __name__ == '__main__':
    main()
