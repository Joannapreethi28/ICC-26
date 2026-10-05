"""Permanent free hosting of the demo + MCP server on Modal (Sir Jabin, 5 Oct 2026).

Deploy:  python -m modal deploy deploy/modal_app.py
URL:     https://<workspace>--make-ai-know-her-web.modal.run   (MCP: <URL>/gradio_api/mcp/)

Same code path as the laptop (scripts/serve_demo.py: trained Laya warm-up checks, MCP icons). Versions pinned to the
laptop's tested environment. Weights come from the public GitHub Release with SHA-256 checks (scripts/get_laya_weights.py).
Cost guard: one small CPU container (max_containers=1) that sleeps after 5 idle minutes; no secrets are used or stored.
Free tier without a card is $1/month (seen on the dashboard 5 Oct): roughly 14 awake hours. When it runs out the app stops; nothing is charged.
"""
import os
import pathlib
import subprocess

import modal

REPO = pathlib.Path(__file__).resolve().parents[1]

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("torch==2.11.0", index_url="https://download.pytorch.org/whl/cpu")
    .pip_install(
        "laya==0.3.24", "transformers==5.18.0", "tokenizers==0.23.2", "safetensors==0.8.0", "huggingface_hub==1.33.0",
        "numpy==2.2.6", "gradio[mcp]==6.29.1", "mcp==1.30.0", "duckdb==1.5.6", "pandas==2.2.2", "pyarrow==23.0.1",
        "requests==2.32.5", "pyyaml==6.0.3", "rapidfuzz==3.14.5", "jinja2==3.1.6", "fastapi==0.135.1", "uvicorn==0.41.0",
    )
    .add_local_file(REPO / "scripts" / "get_laya_weights.py", "/app/scripts/get_laya_weights.py", copy=True)
    .run_commands("python /app/scripts/get_laya_weights.py")
    .env({"PYTHONPATH": "/app/src", "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "GRADIO_ANALYTICS_ENABLED": "False"})
    .add_local_dir(REPO / "src", "/app/src", ignore=["**/__pycache__/**"])
    .add_local_dir(REPO / "data", "/app/data")
    .add_local_dir(REPO / "logo", "/app/logo")
    .add_local_file(REPO / "scripts" / "serve_demo.py", "/app/scripts/serve_demo.py")
)

app = modal.App("make-ai-know-her", image=image)


@app.function(cpu=1.0, memory=3072, max_containers=1, scaledown_window=300, timeout=600)  # ~$0.07/h awake; free tier is $1/mo
@modal.concurrent(max_inputs=16)
@modal.web_server(port=7862, startup_timeout=600)
def web():
    subprocess.Popen(["python", "/app/scripts/serve_demo.py", "--host", "0.0.0.0", "--port", "7862"],
                     cwd="/app", env=dict(os.environ))
