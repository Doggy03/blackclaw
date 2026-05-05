"""宏观政策长链推理 Agent：将非结构化新闻压缩为离散情绪因子。"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_logger = logging.getLogger(__name__)


@dataclass
class MacroReasoningOutcome:
    """宏观推理输出。"""

    sentiment_score: float
    verdict: str
    reasoning_summary: str
    articles_analyzed: int
    proxy_routed: bool


class MacroReasoningAgent:
    """
    读取宏观与行业文本（演示中为占位摘要），产出看多/看空/震荡相关连续情绪分。

    生产环境可将 `reason` 中对 LLM 的调用接到 `api_gateway.yaml` 所描述的代理端点。
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """
        Args:
            config_path: `api_gateway.yaml` 路径；缺省为仓库内 `config/api_gateway.yaml`。
        """

        root = Path(__file__).resolve().parents[1]
        self._config_path = config_path or (root / "config" / "api_gateway.yaml")
        self._cfg: dict[str, Any] = {}

    def load_config(self) -> dict[str, Any]:
        """
        加载网关 YAML。

        Returns:
            配置字典。
        """

        if not self._config_path.exists():
            _logger.warning("Config missing at %s; using defaults", self._config_path)
            return {}
        with self._config_path.open(encoding="utf-8") as f:
            self._cfg = yaml.safe_load(f) or {}
        return self._cfg

    def reason(self, article_count: int = 15) -> MacroReasoningOutcome:
        """
        对宏观新闻做长链推理（演示为启发式占位，可替换为真实 LLM）。

        Args:
            article_count: 参与分析的新闻条数（演示）。

        Returns:
            MacroReasoningOutcome: 情绪分与摘要。
        """

        self.load_config()
        proxy = bool((self._cfg.get("proxy") or {}).get("enabled", False))
        summary = (
            "Real estate financing easing policies expected to marginally improve Q3 steel demand."
        )
        score = 0.65
        verdict = "bullish_bias"
        return MacroReasoningOutcome(
            sentiment_score=score,
            verdict=verdict,
            reasoning_summary=summary,
            articles_analyzed=article_count,
            proxy_routed=proxy,
        )
