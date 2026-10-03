> Status update, 3 October 2026: account/access, model download and local inference
> are complete. This file preserves the original access instructions. See
> `TRANSLATION_SETUP.md` for the measured run and `DATA_CARD.md` for final retention.

# IndicTrans2 access setup

Joanna reports creating her free Hugging Face account, verifying her email and
accepting the model repository's access conditions on 3 October 2026. Terminal
access is not yet verified. This is separate from approving the large download.

Run the prepared helper in normal PowerShell, using the project Python:

```powershell
python eval_data/tools/setup_hf_access.py
```

It installs the official `huggingface_hub==2.1.1` package via pip, starts the
official SDK's `interpreter_login()` browser flow and checks the selected model. Authentication stays in
`.icc-tools/hf-home` beside the repository; no credentials belong in Git or chat.
The helper neither changes Git credentials nor executes downloaded model code.

The first run installed the package successfully but the CLI failed on a missing
`venv` module in Windows embedded Python. The helper now uses the public Python
login API directly, avoiding the CLI's unrelated extension loader. Its regression
test exercises that login entry point with `venv` unavailable and stops at the
browser/network boundary. Actual browser authorization still requires Joanna.

Only small repository files are downloaded for inspection (50 MiB maximum).
The script excludes model weight formats, checks file sizes, records checksums
and pins the model commit. It writes the non-secret result to
`preparation/indictrans2_download_plan.json`. Safetensors weights remain pending.
The preparation tests verify that no weight download is requested by this step.

After it prints `HF access ready`, inspect the downloaded Python/configuration
files, choose compatible runtime packages and ask Joanna before the model download
above 1 GB. Browser consent alone does not authorize that download or a job above
20 minutes. Pin the runtime package versions separately: the CLI version in this
access report is not a claim that translation dependencies have been installed.

References: [official CLI login](https://huggingface.co/docs/huggingface_hub/guides/cli#hf-auth-login),
[Python terminal login](https://huggingface.co/docs/huggingface_hub/package_reference/authentication#huggingface_hub.interpreter_login),
[model](https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M),
[download API](https://huggingface.co/docs/huggingface_hub/package_reference/file_download).
