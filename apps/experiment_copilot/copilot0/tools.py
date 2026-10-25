# -*- coding: utf-8 -*-

# ***************************************************
# * File        : tools.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : Experiment Copilot C0 —— tsproj_ml 只读工具集
# * Requirement : 严格遵守 AGENTS.md §7 安全边界：只读、白名单路径、禁执行
# ***************************************************

# python libraries
import difflib
import json
import os
from pathlib import Path
from typing import Dict, List

# third-party libraries
import pandas as pd

# 目标仓库（可用环境变量 TPROJ_ML_ROOT 覆盖）
TSProj_ROOT = Path(os.environ.get("TPROJ_ML_ROOT", str(Path.home() / "projects" / "tsproj_ml")))
CONFIG_DIR = TSProj_ROOT / "config"
RESULTS_DIR = TSProj_ROOT / "results"

# 单次返回截断，避免撑爆 Agent 上下文
MAX_CHARS = 6000
# 指标列（tsproj_ml test_scores_df.csv 约定）
METRIC_COLUMNS = ["MAE", "RMSE", "Bias", "MAPE", "Accuracy"]


def _resolve_within(base: Path, rel: str) -> Path:
    """
    路径安全：rel 必须落在 base 内，防目录穿越。

    Args:
        base (Path): 允许的根目录
        rel (str): 相对路径

    Returns:
        Path: 解析后的绝对路径
    """
    p = (base / rel).resolve()
    if base.resolve() not in p.parents and p != base.resolve():
        raise ValueError(f"路径越界（仅允许 {base} 内）: {rel}")
    if not p.exists():
        raise FileNotFoundError(f"文件不存在: {rel}")
    return p


def list_configs() -> str:
    """
    列出 tsproj_ml 的全部实验配置 YAML（相对 config/ 的路径）。
    """
    items = sorted(
        str(p.relative_to(CONFIG_DIR)) for p in CONFIG_DIR.rglob("*.y*ml")
    )
    return "\n".join(items) if items else "config/ 下没有 YAML 配置"


def read_config(rel_path: str) -> str:
    """
    读取指定配置 YAML 的文本内容。

    Args:
        rel_path (str): 相对 config/ 的路径，如 aidc_load_5min/outlier_detect.yaml
    """
    p = _resolve_within(CONFIG_DIR, rel_path)
    return p.read_text(encoding="utf-8")[:MAX_CHARS]


def diff_configs(rel_a: str, rel_b: str) -> str:
    """
    对比两个配置 YAML 的差异（unified diff）。
    """
    a = _resolve_within(CONFIG_DIR, rel_a).read_text(encoding="utf-8").splitlines()
    b = _resolve_within(CONFIG_DIR, rel_b).read_text(encoding="utf-8").splitlines()
    diff = "\n".join(difflib.unified_diff(a, b, fromfile=rel_a, tofile=rel_b))
    return (diff or "两个配置完全一致")[:MAX_CHARS]


def list_results(limit: int = 20) -> str:
    """
    列出已有的实验结果目录（result identity，含 result_metadata.json）。
    """
    rows = sorted(
        {
            str(p.parent.relative_to(RESULTS_DIR))
            for p in RESULTS_DIR.rglob("result_metadata.json")
        }
    )
    return "\n".join(rows[-limit:]) if rows else "results/ 下没有实验结果"


def read_result_summary(rel_dir: str) -> str:
    """
    汇总单个结果目录的关键信息：策略、回测几何与平均指标。

    Args:
        rel_dir (str): 相对 results/ 的结果目录路径（来自 list_results）
    """
    d = _resolve_within(RESULTS_DIR, rel_dir)
    meta = json.loads((d / "result_metadata.json").read_text(encoding="utf-8"))
    backtest = meta.get("backtest", {})
    lines = [
        f"identity: {rel_dir}",
        f"strategy: {meta.get('result_method', {}).get('strategy')}",
        f"backtest: windows={backtest.get('window')} "
        f"folds={backtest.get('fold_count')} origin={backtest.get('origin')}",
    ]

    scores = d / "test_scores_df.csv"
    if scores.exists():
        df = pd.read_csv(scores)
        agg = df[df["scope"] == "aggregate"] if "scope" in df.columns else df
        parts = []
        for col in METRIC_COLUMNS:
            if col in agg.columns:
                parts.append(f"{col}={agg[col].mean():.4f}")
        lines.append("mean metrics (aggregate): " + ("  ".join(parts) or "无指标列"))
    else:
        lines.append("mean metrics: 缺少 test_scores_df.csv")

    return "\n".join(lines)[:MAX_CHARS]


class CopilotTools:
    """
    面向 ReAct Agent 的工具适配层：提供 toolConfig（描述）与 call（分发），
    接口与 learn.level1_from_scratch.react.tool.Tools 一致。
    """

    def __init__(self) -> None:
        self.toolConfig = self._tools()

    def _tools(self) -> List[Dict]:
        return [
            {
                "name_for_human": "实验配置列表",
                "name_for_model": "list_configs",
                "description_for_model": "列出 tsproj_ml 仓库 config/ 下的全部实验配置 YAML 路径。",
                "parameters": [],
            },
            {
                "name_for_human": "读取配置",
                "name_for_model": "read_config",
                "description_for_model": "读取指定实验配置 YAML 的完整内容。先用 list_configs 拿到路径。",
                "parameters": [
                    {
                        "name": "rel_path",
                        "description": "相对 config/ 的路径",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                ],
            },
            {
                "name_for_human": "结果目录列表",
                "name_for_model": "list_results",
                "description_for_model": "列出 tsproj_ml 已有实验结果目录（模型-策略标识）。",
                "parameters": [],
            },
            {
                "name_for_human": "结果摘要",
                "name_for_model": "read_result_summary",
                "description_for_model": "读取单个实验结果的策略、回测几何与平均指标（MAE/RMSE/MAPE/Accuracy）。先用 list_results 拿到目录。",
                "parameters": [
                    {
                        "name": "rel_dir",
                        "description": "相对 results/ 的结果目录路径",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                ],
            },
        ]

    def call(self, name: str, **kwargs) -> str:
        """
        按工具名分发调用（白名单内的只读操作）。
        """
        dispatcher = {
            "list_configs": list_configs,
            "read_config": read_config,
            "list_results": list_results,
            "read_result_summary": read_result_summary,
        }
        if name not in dispatcher:
            return f"未知工具: {name}，可用工具: {list(dispatcher)}"
        try:
            return dispatcher[name](**kwargs)
        except (ValueError, FileNotFoundError) as e:
            return f"工具调用失败: {e}"


# 测试代码 main 函数
def main():
    print(list_configs()[:500])
    print("-" * 40)
    print(list_results(limit=5))
    print("-" * 40)
    print(
        read_result_summary(
            "results_test/aidc_hvac_load_5min/baseline/hvac_all_devices/"
            "route_A/ALL/lightgbm-dirmo-local-k1-ae694a6748b4/backtest_only"
        )
    )


if __name__ == "__main__":
    main()
