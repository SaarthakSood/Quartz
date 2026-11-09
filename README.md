---
title: QuartZ
emoji: 💎
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# QuartZ

Detects AI-generated **images and videos**. FastAPI backend, single-file frontend, installable as a desktop app.

## Use it like a desktop app
**Easiest (Windows):** double-click `QuartZ.bat`. **Mac/Linux:** `./quartz.sh`.
First run creates a virtual environment and installs everything (~1 GB, once). After that it starts the server and opens QuartZ in its own window (Chrome/Edge/Brave app mode, no tabs). Closing the window stops the server.

**Or install it from the browser (PWA):** run the server (`python run_desktop.py` or the Space URL), open it in Chrome/Edge, then use the install icon in the address bar or the "Install QuartZ as an app" button. It gets its own window, taskbar/Start menu icon and opens offline (checking files still needs the server).

## Experimental V3 score (separate)
The bundled Unified V3 classifier (`models/`, ~60% on the Argus benchmark) shows its own score under the main result. It is never part of the average, verdict or conflict check. Set `QUARTZ_EXTRA=` (empty) to hide it, or point it at another `v3:<path>.joblib`.

## Features
- Drop, paste (`Ctrl+V`) or open (`Ctrl+O`) an image or video. Type is detected automatically.
- Images: PNG/JPEG/WebP up to 12 MB. Videos: MP4/WebM/MOV up to 60 MB, ~10 frames sampled.
- Two pretrained detectors are averaged into one AI probability (≤35% likely real, 35–65% can't tell, ≥65% likely AI).
- 10 themes. Dark: Obsidian, Smoky quartz, Amethyst, Rose noir, Aventurine. Light: Clear quartz, Rose quartz, Citrine, Chalcedony, Lilac. The sun button flips between your last dark and light theme; the palette button opens the full list. Defaults to your system's light/dark setting.
- The crystal changes colour with the verdict. Recent checks are kept in your browser only (name and score, never the file).

Scores are **uncalibrated** and not proof. Detectors miss new generators and are fooled by screenshots, edits and heavy compression.

## Run manually
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements-dev.txt
python run_desktop.py            # or: uvicorn backend.app:app --port 7860
python -m pytest -q tests        # no model download needed
```
First start downloads model weights (~0.5 GB); the sidebar shows "Loading models…" then "Engine ready".

## Guide (PDF)
`docs/QuartZ_Guide.pdf` has install steps, how to share it with friends, datasets, and training approaches.

## Train your own model
`training/` has `prepare_data.py` (build data/train + data/val), `train_classic.py` (Gaussian NB, Gaussian Mixture, Decision Tree, Random Forest, SVM... on forensic features, runs on CPU) and `train_finetune.py` (fine-tune a ViT on a GPU / Colab). `pip install -r requirements-train.txt` first. Details in the PDF.

## Pick the best models for your images
`python compare_models.py data` scores every candidate detector separately on your `data/ai` + `data/real` images (accuracy, AUC, confusion matrix) and prints the best combination plus the `QUARTZ_MODELS=` line to use. The old second model (Organika/sdxl-detector) only knows SDXL images, so it is no longer a default.

## Measure accuracy (confusion matrix)
Put labelled images in `data/ai/` and `data/real/`, then `python evaluate.py data 0.5`.

## Config (env vars)
| var | default | meaning |
|---|---|---|
| `QUARTZ_MODELS` | `Ateeqq/ai-vs-human-image-detector,haywoodsloan/ai-image-detector-deploy` | comma-separated Hugging Face image-classification model ids |
| `QUARTZ_VIDEO_FRAMES` | 10 | frames sampled per video |
| `QUARTZ_WEIGHTS` | equal | per-model weights in the same order, e.g. `1,0.5` (`0` switches a model off) |
| `QUARTZ_AI_LABELS` / `QUARTZ_REAL_LABELS` | - | extra label names for unusual checkpoints, e.g. `label_1` / `label_0` |
| `QUARTZ_THREADS` | CPU count | torch threads |
| `QUARTZ_PORT` | 7860 | desktop launcher port |
| `QUARTZ_NO_WINDOW` | unset | `1` = server only, no window |

Use your own fine-tuned model: push it to the Hub and set `QUARTZ_MODELS=you/your-model`. Labels need a recognisable word (`ai`, `artificial`, `fake`, `generated` / `real`, `human`, `hum`, `natural`). Old `VERITAS_*` names still work.

## Sharing with friends
- **Free temporary link from your PC:** start QuartZ, then in a second terminal run `cloudflared tunnel --url http://localhost:7860` (install: `winget install Cloudflare.cloudflared` / `brew install cloudflared`). Send the printed `trycloudflare.com` link. It works only while your PC is on, and anyone with the link can use it.
- **Zip:** friends unzip and double-click `QuartZ.bat` (Windows) or run `./quartz.sh`.
- **Hugging Face Space (Docker SDK):** the repo is ready for it (README front matter + Dockerfile, port 7860), but Hugging Face's current docs say compute-backed Spaces need a paid plan; check the New Space page first. Pushing a trained *model* to the Hub is separate and free.

## Live pipeline and crystal (2.0)

- **Live pipeline dashboard** (under the upload area) shows the real stages of each check: received, preprocessing,
  feature extraction, model analysis, classification, final result. Every status, duration, resolution, file size,
  embedding dimension and model score comes from an event the server emitted while doing that work. Nothing is simulated.
- **Transport:** Server-Sent Events. The page picks a job id, opens `GET /api/events/<job>`, then posts the file to
  `/api/image?job=<job>` or `/api/video?job=<job>`. Without `?job=` the endpoints behave exactly as before.
  Event shape: `{"seq", "t", "stage", "status", "message", ...}` with `status` in `pending|processing|completed|failed|skipped`.
  Model rows add `model`, `ai_probability`, `duration_ms`; video events add `frame`/`frames`.
- **Feature extraction** is only a visible stage when a standalone extractor runs (the experimental V3 DINOv2 scorer).
  Otherwise it is shown as *Skipped*; the two Hugging Face pipelines do their resize/normalise/feature steps internally.
- **Crystal:** a dependency-free WebGL renderer (`frontend/static/crystal.js`): refraction with dispersion, internal
  bounce, Fresnel reflections, facet edges, purple/blue/cyan lighting. It spins up while processing, settles on
  completion, tints to the verdict, and turns red on error. Falls back to the previous SVG gem if WebGL is unavailable.
  Low-power GPU hint, DPR capped at 1.5, ~30 fps when idle, paused when hidden/off-screen.

## Crystal activity response (QuartZ 2.0 update)

The WebGL crystal now responds to the real Server-Sent Events emitted by the
analysis backend. The frontend maps received, preprocessing, feature extraction,
model analysis, classification, and terminal events to a bounded activity level.
That level smoothly controls rotation speed, inner glow, and pulse intensity.
Video frame metadata and individual model activity can add intensity while the
corresponding work is actually running. There is no elapsed-time progress
simulation; if live events are unavailable, the crystal retains its safe default
processing animation and the analysis result is unaffected.

### Live detail (2.1)
- While the server works it sends a **tick every 0.5 s** (`kind:"tick"`: `elapsed_ms`, `cpu_pct`, `rss_mb`, current `model` and `step`) and a **step** event whenever a real sub-step starts (`kind:"step"`: `Loading weights`, `Preprocessing`, `Forward pass`, `Softmax and labels`, DINOv2 / classifier head for V3). These have `status:"live"` and never change a stage's state.
- A `queue` event is sent when all inference slots are busy (`processing` -> `completed`).
- SSE events carry `id:` and `Last-Event-ID` resumes after a reconnect. Proxies that buffer SSE are handled by a 2 KB flush comment plus a **polling fallback**: `GET /api/jobs/<job>?after=<seq>` returns `{events, done}`. The page switches to it automatically after 2.5 s of silence and always collects the full trace when the request ends.
- `psutil` (optional but in requirements) gives memory numbers on every OS.
