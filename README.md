# IronClaw Macro Agent

An AI-driven quantitative and qualitative research system designed for the black metals commodity market (Iron Ore, Steel Rebar, Coke PCI).

This repository implements the **Python research pipeline** (data scraping, macro reasoning hooks, RF signal fusion, vector snapshot persistence). **[OpenClaw](https://docs.openclaw.ai/) is a separate self-hosted Gateway** (Node/npm) for multi-agent routing and channels; pair it when you want the Gateway to orchestrate personas and tools outside this codebase.

## Architecture

| Layer | Role |
| :--- | :--- |
| **OpenClaw Gateway** | Runs on Node.js (`npm install -g openclaw@latest`); exposes Control UI and multi-agent isolation. Docs: [openclaw.ai](https://docs.openclaw.ai/). |
| **LLM Gateway (this repo)** | `config/api_gateway.yaml` describes your VPS Nginx reverse proxy and provider env-vars (never commit secrets). Macro Agent reads this schema to align with routed API calls. |
| **Vector Store (optional)** | Chroma persistent client under `.chroma/` when `requirements-vectors.txt` is installed. |
| **ML** | `RandomForestRegressor` baseline fused with Macro sentiment in `agents/report_synthesizer.py`. |

## Core workflows

1. **Data ingestion** — Scraped structured exchange-style fields plus basis tails; summarized for embedding (`DataScraperAgent.build_embedding_text`).
2. **Policy reasoning** — `MacroReasoningAgent` placeholders for chain-of-policy analysis (swap in Anthropic/other clients via gateway config).
3. **Vector snapshots** — `ingest.vector_store.VectorMemory` upserts one doc per calendar day keyed by basis tail text.
4. **Synthesis** — RF prediction + sentiment overlay; `ExecutionAgent` log line points at the daily PDF path under `outputs/reports/`.

## Quick start (Python)

```bash
cd IronClaw-Macro-Agent
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-vectors.txt             # optional: real Chroma upserts
python scripts/train_stub_model.py                  # optional: non-empty models/random_forest_basis.pkl
python run_daily_workflow.py
```

Configure `config/api_gateway.yaml` with env-based keys.

Draft application copy for questionnaire item #04 lives in **`APPLICATION_Q04_en.md`** (English).

### Publish this repo to GitHub

After `git` history exists locally (`main`):

```bash
export GITHUB_OWNER="your-github-username"
export GITHUB_TOKEN="ghp_xxxxxxxx"              # PAT with repo scope
bash scripts/publish_to_github.sh              # delegates to scripts/_github_publish.py
```

## OpenClaw Gateway (Node/npm)

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
openclaw dashboard
```

Typical pattern: keep this repo on a server and trigger `run_daily_workflow.py` via `cron`/systemd; use OpenClaw for interactive agent routing alongside the batch pipeline.

## Repository layout

- `agents/` — Data scraper, macro reasoning, quantitative fusion
- `ingest/` — Chroma-backed `VectorMemory`
- `config/` — API gateway, optional vector YAML, Gateway placeholder JSON (no secrets)
- `models/` — `random_forest_basis.pkl` (empty commits trigger auto-train on first run)
- `scripts/` — `fetch_inventory_data.py`, `train_stub_model.py`

## License

MIT (replace if you prefer another license.)
