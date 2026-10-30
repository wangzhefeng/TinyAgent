# -*- coding: utf-8 -*-

# ***************************************************
# * File        : baselines.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : Survey Agent —— 数据集与真实基线评测（无外部模型依赖）
# ***************************************************

# python libraries
import math
import random
from typing import Dict, List

# global variable
SEASON = 12
N_TOTAL = 240
SERIES = [
    round(
        50 + 0.15 * t                          # 趋势
        + 10 * math.sin(2 * math.pi * t / SEASON)   # 季节
        + random.Random(t).gauss(0, 2),        # 噪声（确定性种子）
        3,
    )
    for t in range(N_TOTAL)
]
TRAIN, TEST = SERIES[:-24], SERIES[-24:]


def describe_dataset() -> str:
    """数据集描述（供 agent 决定评测设计）。"""
    return (
        f"合成月度负荷序列：{N_TOTAL} 点（训练 {len(TRAIN)} / 留出测试 {len(TEST)}），"
        f"含线性趋势 + 周期 {SEASON} 的季节性 + 高斯噪声；"
        f"训练集均值 {sum(TRAIN) / len(TRAIN):.1f}，"
        f"测试集前 12 点示例 {TEST[:12]}。"
    )


def _forecast(method: str, horizon: int) -> List[float]:
    """三个基线的确定性实现。"""
    if method == "naive":
        return [TRAIN[-1]] * horizon
    if method == "seasonal":
        return [TRAIN[-SEASON + (i % SEASON)] for i in range(horizon)]
    if method == "ma":
        window = TRAIN[-SEASON:]
        avg = sum(window) / len(window)
        return [avg] * horizon
    raise ValueError(f"未知基线: {method}（可用: naive/seasonal/ma）")


def run_baselines(horizon: int, methods: str) -> str:
    """真实执行基线评测并返回指标表（MAE/RMSE）。"""
    horizon = min(max(int(horizon), 1), len(TEST))
    names = [m.strip() for m in methods.split(",") if m.strip()]
    rows = ["| 基线 | MAE | RMSE |", "|---|---|---|"]
    for name in names:
        preds = _forecast(name, horizon)
        errs = [p - a for p, a in zip(preds, TEST[:horizon])]
        mae = sum(abs(e) for e in errs) / len(errs)
        rmse = math.sqrt(sum(e * e for e in errs) / len(errs))
        rows.append(f"| {name} | {mae:.3f} | {rmse:.3f} |")
    rows.append(f"（horizon={horizon}，测试真值前 5 点 {TEST[:5]}）")
    return "\n".join(rows)


def dataset_stats() -> Dict:
    """数据集统计（供报告引用）。"""
    return {
        "n_total": N_TOTAL,
        "n_train": len(TRAIN),
        "n_test": len(TEST),
        "season": SEASON,
    }
