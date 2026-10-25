# -*- coding: utf-8 -*-

# ***************************************************
# * File        : models_meta.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : Survey Agent —— 时序基础模型元数据（调研阶段输入材料）
# ***************************************************

# python libraries

# global variable
MODELS_META = [
    {
        "name": "Time-MoE",
        "paper": "Time-MoE: Billion-Scale Time Series Foundation Models with Mixture of Experts (arXiv:2409.16040)",
        "method": "十亿参数级混合专家（MoE）时序基础模型；稀疏激活降低训练/推断成本，"
        "支持任意长度上下文的前缀因果建模，多分辨率预测。",
        "paradigm": "点预测；大规模预训练 + 下游零样本/微调",
    },
    {
        "name": "Chronos",
        "paper": "Chronos: Learning the Language of Time Series (Amazon, arXiv:2403.07815)",
        "method": "把标量序列按均值缩放量化为离散 token，直接用 T5 类语言模型架构做"
        "自回归生成；概率预测（可采样多条未来轨迹）。",
        "paradigm": "概率预测；零样本能力强",
    },
    {
        "name": "TimesFM",
        "paper": "A decoder-only foundation model for time-series forecasting (Google, arXiv:2310.10688)",
        "method": "decoder-only 前缀架构（input patch 前缀 + 预测头多步直接输出）；"
        "在大量合成+真实语料上预训练，主打零样本点预测。",
        "paradigm": "点预测；直接多步输出",
    },
]
