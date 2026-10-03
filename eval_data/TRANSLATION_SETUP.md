# Translation installation and measured run, 3 October 2026

HF access is confirmed. The inspected model revision is
`173b94239f7c38886b2747b8d4a5db771a7e1232` of
`ai4bharat/indictrans2-en-indic-dist-200M`. The 14 small files match their recorded
sizes and SHA-256 hashes. Model weights were downloaded and verified: exactly
**1,098,427,592 bytes**, downloaded once as `model.safetensors`.

`tools/setup_indictrans_runtime.py` prints the plan without network access by
default. After Joanna approves the large download, `--approved-download` installs
the pinned packages from `indictrans-runtime-requirements.txt` in the separate
workspace `.icc-tools/indictrans-runtime`, downloads the single pinned weight file,
checks its SHA-256 against Hub metadata, and records actual package versions and
source hashes. The estimated package download is another 0.3–0.6 GB. Model files,
package binaries and credentials are not committed. This helper runs no inference.

## Compatibility choice and review

- The modern IndicTransToolkit release provides Linux/macOS wheels and explicitly
  says Windows is not supported. Avoid a compiler/build-tool installation for this
  prototype. Use the publisher's pure-Python `IndicProcessor` from commit
  `0e68fb5872f4d821578a5252f90ad43c9649370f`, loaded as a standalone source module.
- Keep the current tokenizer shipped with the model. Do **not** use the deprecated
  custom tokenizer from that older toolkit commit. Pre/postprocessing still uses
  its language tags, Moses normalization, entity placeholders, and Indic script
  conversion. Only English-to-Hindi/Tamil with one output per input is in scope.
- Pin CPU Torch 2.6.0, Transformers 4.51.3, NumPy 2.2.6, SentencePiece 0.2.0,
  Sacremoses 0.1.1 and upstream Indic NLP Library 0.92. This combination passed local imports, preprocessing and actual Hindi/Tamil
  generation. Installation provenance is in `preparation/indictrans2_install.json`.
- The inference Hub SDK stays in this separate directory; the device-login SDK
  2.1.1 remains in the original environment. Local inference must use offline
  loading, CPU float32, no FlashAttention and the recorded source hashes.
- Static inspection covered imports, top-level execution and file/network/process
  operations in the three downloaded custom Python modules. The configuration and
  modeling files import Torch/Transformers and define the model; tokenizer reads
  local JSON/SentencePiece data and has explicit save methods. No direct network,
  shell, process-launch or deletion calls were found. The processor source was
  inspected from the publisher's pinned GitHub revision; it performs text
  normalization and placeholder handling. This is not a full third-party audit.

Joanna approved the large download/install. A four-output compatibility/speed pilot
passed, followed by 370 main outputs (248.98 seconds generation, 1.58 seconds model
load) and 85 reserve outputs (56.08 seconds generation, 1.30 seconds model load).
Both jobs were estimated below 20 minutes; no long-job approval was needed.
Final semantic selection retains 300 NLU and 68 benchmark translations. Raw outputs
and rejected/unused candidates remain in preparation files. No output was rewritten
and mislabelled as model output. One same-agent reviewer; no native-speaker review.

Re-run the exact main requests locally (existing valid outputs are reused):

```powershell
python eval_data/tools/translate.py --input eval_data/preparation/translation_requests.jsonl --output eval_data/preparation/translation_output.jsonl
```

The runner verifies all downloaded source/weight checksums before importing model
code, uses the separate runtime first on `sys.path`, and loads offline. Each output
is flushed after its batch. Resume signatures bind exact inputs, model installation,
threads and generation parameters. Inputs over 256 tokens are rejected without
truncation; outputs that hit the generation limit are ineligible for release.
Changing a request or settings cannot silently reuse an old output.

On another Windows/Python 3.11 machine, recreate the isolated runtime with the
prepared setup helper after accepting the model terms. Keep credentials local.
Do not execute a job exceeding 20 minutes without Joanna's approval.

References: [model and usage](https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M),
[toolkit release notes](https://github.com/VarunGumma/IndicTransToolkit/blob/main/CHANGELOG.md),
[pinned processor](https://github.com/VarunGumma/IndicTransToolkit/blob/0e68fb5872f4d821578a5252f90ad43c9649370f/IndicTransTokenizer/processor.py),
[toolkit Windows limitation](https://pypi.org/project/indictranstoolkit/),
[Indic NLP 0.92 metadata](https://pypi.org/pypi/indic-nlp-library/0.92/json),
[official CPU Torch wheels](https://download.pytorch.org/whl/cpu/torch/).
