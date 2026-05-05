# Question 04 — Concrete outcomes from Agents / AI-driven construction (draft answer, English)

This project delivers an **automated black-metals research and basis-trading signal stack** focused on **iron ore, rebar, and coke PCI**, combining a **self-hosted OpenClaw Gateway (Node.js)** for **multi-agent routing and session isolation** with a **Python research pipeline** that ingests quantitative market structure and transforms qualitative macro narratives into actionable factors.

Core pain solved: discretionary commodity research suffers from **severely fragmented data**. Classic Python scrapers excel at normalized exchange inventories and outright prices but struggle to align **rapidly evolving Chinese macro and real-estate financing policies** with forward-looking procurement and basis opportunities. Manual reading creates **acute latency** versus fast-moving spreads.

Architecturally, OpenClaw runs as the **operational gateway**: it models how distinct agent personas interoperate outside a single brittle chat transcript. Alongside it, Python implements modular agents and reproducible workflows.

**Workflow (multi-agent, long-chain reasoning):**

1. **Data Agent** — Pulls normalized spot/stacking/basis-aligned frames (demo uses synthetic stubs; wire to your exchange feeds). It emits a **compact tail snapshot** for embedding.

2. **Vector memory (Chroma, optional)** — Persists daily structured snapshots to a **persistent vector index** so later macro analyses can retrieve comparable inventory/basis regimes.

3. **Macro-Policy Agent** — Consumes routed LLM requests through **`config/api_gateway.yaml`**, which documents a **VPS-hosted Nginx reverse proxy** tuned for dependable, concurrent **Anthropic-compatible** endpoints. Outputs a **bullish/bearish/range-bound style sentiment score** annotated with rationale.

4. **Quant Agent** — Loads a **Random Forest** regression baseline for spreads/basis regimes, then **re-weights forecasts** using the Macro agent’s sentiment signal.

5. **Execution Agent** — Emits an auditable narrative thread and resolves a **daily briefing artifact path** (`outputs/reports/BlackMetal_Daily_YYYYMMDD.pdf` in demo mode).

Operational proof is trivial to reproduce locally: **`python run_daily_workflow.py`** prints orchestrated logs (**OpenClaw-Orchestrator → DataAgent → VectorStoreAgent → MacroAgent → QuantAgent → ExecutionAgent**) that mirror multi-agent choreography and compress the latency from ingestion to synthesized signal.

End-to-end, the lineage is intentionally **auditable**: each hop names the responsible agent, infrastructure contracts live in **YAML plus environment variables** (no secrets in git), and vector dependencies remain **optional** so CI or air-gapped laptops still execute the quant path.

The design deliberately keeps Gateway concerns **orthogonal** to reproducible notebooks and CI-friendly Python tests.
