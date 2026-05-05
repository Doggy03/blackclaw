"""报告与信号合成 Agent：随机森林基准 + LLM 情绪权重调整。"""

from __future__ import annotations

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

_logger = logging.getLogger(__name__)


@dataclass
class QuantSignal:
    """量化融合后的信号结构。"""

    ml_baseline: float
    sentiment_adjusted: float
    model_path: Path
    notes: str


class ReportSynthesizer:
    """
    加载（或训练占位）随机森林模型，将 Macro Agent 情绪分并入预测，并生成日报路径提示。
    """

    def __init__(self, model_path: Path | None = None) -> None:
        """
        Args:
            model_path: `random_forest_basis.pkl` 路径。
        """

        root = Path(__file__).resolve().parents[1]
        self._model_path = model_path or (root / "models" / "random_forest_basis.pkl")

    def _load_or_train_model(self) -> RandomForestRegressor:
        """
        若 pkl 不存在或损坏，则训练一棵极小随机森林用于演示。

        Returns:
            拟合后的 RandomForestRegressor。
        """

        if self._model_path.exists() and self._model_path.stat().st_size > 0:
            try:
                with self._model_path.open("rb") as f:
                    return pickle.load(f)
            except (pickle.UnpicklingError, EOFError):
                _logger.warning("Corrupt or empty pickle; retraining stub model.")
        X = np.random.default_rng(0).normal(size=(200, 5))
        y = X[:, 0] * 0.5 + X[:, 1] * -0.2 + np.random.default_rng(1).normal(scale=0.1, size=200)
        model = RandomForestRegressor(n_estimators=20, random_state=42)
        model.fit(X, y)
        self._model_path.parent.mkdir(parents=True, exist_ok=True)
        with self._model_path.open("wb") as f:
            pickle.dump(model, f)
        return model

    def fuse(
        self,
        features: pd.DataFrame,
        sentiment_score: float,
        sentiment_weight: float = 0.15,
    ) -> QuantSignal:
        """
        将情绪分叠加到 ML 基准预测上。

        Args:
            features: 与模型训练维数一致的特征表（演示取末行或均值）。
            sentiment_score: [-1, 1] 或业务约定的情绪分。
            sentiment_weight: 情绪对最终输出的线性权重。

        Returns:
            QuantSignal: 基准与调整后的数值。
        """

        model = self._load_or_train_model()
        n_features = getattr(model, "n_features_in_", 5)
        if features.shape[1] >= n_features:
            x = features.iloc[-1, :n_features].to_numpy().reshape(1, -1)
        else:
            pad = np.zeros((1, n_features))
            pad[0, : features.shape[1]] = features.mean(axis=0).to_numpy()
            x = pad
        baseline = float(model.predict(x)[0])
        adjusted = baseline + sentiment_weight * float(sentiment_score)
        return QuantSignal(
            ml_baseline=baseline,
            sentiment_adjusted=adjusted,
            model_path=self._model_path,
            notes="Stub fusion: linear overlay on RF output.",
        )

    def daily_briefing_path(self, date_str: str) -> Path:
        """
        生成演示用日报输出路径（不实际写 PDF，仅用于 orchestrator 日志）。

        Args:
            date_str: 日期字符串，如 20260505。

        Returns:
            目标报告路径。
        """

        root = Path(__file__).resolve().parents[1]
        out = root / "outputs" / "reports" / f"BlackMetal_Daily_{date_str}.pdf"
        out.parent.mkdir(parents=True, exist_ok=True)
        return out
