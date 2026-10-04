"""REST API, demo and MCP on one local server: python -m mak.api.app."""
from fastapi import FastAPI
from mak.api.service import ResolveRequest, coverage, health, list_supported_intents, resolve_sports_query

app = FastAPI(title='Make AI Know Her', version='0.1.0')

@app.post('/resolve')
def resolve_endpoint(req: ResolveRequest) -> dict:
    return resolve_sports_query(req.query, req.lang)

@app.get('/intents')
def intents_endpoint() -> dict:
    return {'intents': list_supported_intents()}

app.get('/coverage')(coverage)
app.get('/health')(health)

def create_app() -> FastAPI:
    """Mount after REST routes so /resolve and /health remain reachable."""
    import gradio as gr
    from mak.ui.demo import build_demo, CUSTOM_CSS, THEME
    if not getattr(app.state, 'demo_mounted', False):
        gr.mount_gradio_app(app, build_demo(), path='/', mcp_server=True,
                           theme=THEME, css=CUSTOM_CSS)
        app.state.demo_mounted = True
    return app

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(create_app(), host='127.0.0.1', port=8000)
