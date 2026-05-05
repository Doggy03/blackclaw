"""基于 Pandas/Requests 的库存与公开数据抓取脚本骨架。"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_placeholder(url: str, timeout: int = 15) -> pd.DataFrame:
    """
    发起 HTTP GET 并将 JSON 转为 DataFrame（演示：失败时返回空表）。

    Args:
        url: 目标 API 或静态 JSON 地址。
        timeout: 请求超时秒数。

    Returns:
        解析后的 DataFrame，失败时为 empty。
    """

    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return pd.DataFrame(resp.json())
    except (requests.RequestException, ValueError) as e:
        logger.warning("Fetch failed (%s); returning empty DataFrame.", e)
        return pd.DataFrame()


def main() -> None:
    """CLI 入口：示例拉取占位 URL。"""
    parser = argparse.ArgumentParser(description="Fetch commodity inventory stub.")
    parser.add_argument(
        "--url",
        default="https://httpbin.org/json",
        help="JSON endpoint for demo (override with real exchange API).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "outputs" / "raw_inventory.csv",
        help="Output CSV path.",
    )
    args = parser.parse_args()
    df = fetch_placeholder(args.url)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if not df.empty:
        df.to_csv(args.out, index=False)
        logger.info("Wrote %s rows to %s", len(df), args.out)
    else:
        logger.info("No data to write.")


if __name__ == "__main__":
    main()
