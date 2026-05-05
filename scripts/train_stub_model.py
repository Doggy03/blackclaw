#!/usr/bin/env python3
"""
训练占位随机森林并将模型写入 `models/random_forest_basis.pkl`。

在已安装 ``requirements.txt`` 的环境中::

    python scripts/train_stub_model.py
"""

from __future__ import annotations

import pickle
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestRegressor


def main() -> int:
    """
    使用合成数据训练小模型。

    Returns:
        退出码 ``0`` 表示成功写入。
    """
    root = Path(__file__).resolve().parents[1]
    dest = root / "models" / "random_forest_basis.pkl"
    dest.parent.mkdir(parents=True, exist_ok=True)
    rng0 = np.random.default_rng(0)
    rng1 = np.random.default_rng(1)
    x_rows = rng0.normal(size=(200, 5))
    y = x_rows[:, 0] * 0.5 + x_rows[:, 1] * -0.2 + rng1.normal(scale=0.1, size=200)
    model = RandomForestRegressor(n_estimators=20, random_state=42)
    model.fit(x_rows, y)
    dest.write_bytes(pickle.dumps(model))
    print("Wrote:", dest, "(" + str(dest.stat().st_size) + " bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
