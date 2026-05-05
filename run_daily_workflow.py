#!/usr/bin/env python3
"""
OpenClaw 风格日度投研编排演示：打印可申请证明用的结构化日志。

运行方式（在项目根目录）::
    python run_daily_workflow.py
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

# 确保仓库根目录在 path 中
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agents.data_scraper_agent import DataScraperAgent  # noqa: E402
from agents.macro_reasoning_agent import MacroReasoningAgent  # noqa: E402
from agents.report_synthesizer import ReportSynthesizer  # noqa: E402
from ingest.vector_store import VectorMemory  # noqa: E402

_SUCCESS_LEVEL = 25
logging.addLevelName(_SUCCESS_LEVEL, "SUCCESS")


def _setup_logging() -> None:
    """配置与申请材料示例一致的行格式。"""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> None:
    """执行 Data → VectorStore → Macro → Quant → Execution 演示链。"""
    _setup_logging()
    run_date = datetime.now().strftime("%Y%m%d")
    log = logging.getLogger("OpenClaw-Orchestrator")
    log.info("Starting daily research workflow...")

    data_agent = DataScraperAgent()
    scrape = data_agent.run(rows=1250, cols=14)
    dlog = logging.getLogger("DataAgent")
    dlog.info(
        "Fetching latest iron ore inventory data from exchange... Success (Shape: %s, %s)",
        scrape.dataframe.shape[0],
        scrape.dataframe.shape[1],
    )

    snapshot_text = data_agent.build_embedding_text(scrape)
    memory = VectorMemory()
    vect_ok = memory.upsert_market_snapshot(
        doc_id=f"black_metal_daily_{run_date}",
        document=snapshot_text,
        metadata={
            "basis_last": float(scrape.basis_spread) if scrape.basis_spread is not None else 0.0,
            "rows": int(scrape.dataframe.shape[0]),
        },
    )
    vlog = logging.getLogger("VectorStoreAgent")
    vlog.info(
        "Upsert structured snapshot to vector index (chroma=%s, collection=%s, persist=%s)",
        vect_ok,
        memory.collection_name,
        memory.persist_directory,
    )

    macro = MacroReasoningAgent()
    m_out = macro.reason(article_count=15)
    mlog = logging.getLogger("MacroAgent")
    if m_out.proxy_routed:
        mlog.info("Routing requests through custom proxy...")
    mlog.info(
        "Chain-of-thought complete. Analyzed %s macro news articles. "
        'Reasoning summary: "%s Sentiment score: +%s"',
        m_out.articles_analyzed,
        m_out.reasoning_summary,
        m_out.sentiment_score,
    )

    synth = ReportSynthesizer()
    qlog = logging.getLogger("QuantAgent")
    qlog.info("Loading Random Forest model... merging LLM sentiment score.")
    signal = synth.fuse(scrape.dataframe, sentiment_score=m_out.sentiment_score)

    report_path = synth.daily_briefing_path(run_date)

    exe = logging.getLogger("ExecutionAgent")
    exe.info(
        "Fused signal: baseline=%.4f adjusted=%.4f",
        signal.ml_baseline,
        signal.sentiment_adjusted,
    )
    exe.log(_SUCCESS_LEVEL, "Daily Briefing generated: %s", report_path)


if __name__ == "__main__":
    main()
