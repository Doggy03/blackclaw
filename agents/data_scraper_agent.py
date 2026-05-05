"""数据抓取 Agent：交易所/公开结构化数据模拟拉取与基差预处理。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class ScrapeResult:
    """单次抓取结果容器。"""

    dataframe: pd.DataFrame
    basis_spread: float | None
    metadata: dict[str, Any]


class DataScraperAgent:
    """
    负责模拟或对接真实行情/仓单接口，清洗后供 Quant 与其它 Agent 消费。

    Note:
        演示仓库内使用合成数据占位；接入生产时请替换 `_fetch_exchange_frame`。
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """
        Args:
            config_path: 可选配置文件路径。
        """

        self._config_path = config_path

    def run(self, rows: int = 1250, cols: int = 14) -> ScrapeResult:
        """
        执行抓取与基差预处理。

        Args:
            rows: 模拟数据行数（演示用）。
            cols: 模拟数据列数（演示用）。

        Returns:
            ScrapeResult: 清洗后的 DataFrame 与粗略基差价。
        """

        df = self._fetch_exchange_frame(rows=rows, cols=cols)
        basis = float(df["basis_spread"].iloc[-1]) if "basis_spread" in df.columns else None
        meta = {"source": "synthetic_exchange_stub", "rows": len(df)}
        return ScrapeResult(dataframe=df, basis_spread=basis, metadata=meta)

    def build_embedding_text(self, result: ScrapeResult) -> str:
        """
        将最近一次抓取末尾行压缩为可被向量库入库的短文。

        Args:
            result: :class:`ScrapeResult`。

        Returns:
            中英文混合的可读快照字符串。
        """
        tail = result.dataframe.iloc[-1]
        parts = []
        if result.basis_spread is not None:
            parts.append(f"basis_last={result.basis_spread:.6f}")
        core = ["close", "volume", "inventory", "warehouse_receipts"]
        for col in core:
            if col in tail.index:
                parts.append(f"{col}={float(tail[col]):.6f}")
        head = "[black-metal] commodity snapshot tail row | "
        return head + " | ".join(parts)

    def _fetch_exchange_frame(self, rows: int, cols: int) -> pd.DataFrame:
        """
        生成演示用结构化盘面/库存数据矩阵。

        Args:
            rows: 行数。
            cols: 列数。

        Returns:
            含基差序列等列的 pandas DataFrame。
        """

        rng = np.random.default_rng(42)
        base_cols = ["open", "high", "low", "close", "volume", "inventory", "warehouse_receipts"]
        extra = [f"feat_{i}" for i in range(max(0, cols - len(base_cols) - 1))]
        colnames = base_cols + extra + ["basis_spread"]
        data = rng.normal(size=(rows, len(colnames)))
        return pd.DataFrame(data, columns=colnames)
