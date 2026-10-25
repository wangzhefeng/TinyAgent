# -*- coding: utf-8 -*-

# ***************************************************
# * File        : memory.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-11-23
# * Version     : 1.0.112321
# * Description : description
# * Link        : link
# * Requirement : 相关模块版本需求(例如: numpy >= 2.1.0)
# ***************************************************

# python libraries
import os
import sys
from pathlib import Path
ROOT = str(Path.cwd())
if ROOT not in sys.path:
    sys.path.append(ROOT)
import warnings
warnings.filterwarnings("ignore")
from typing import List, Dict, Any, Optional

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


class Memory:
    """
    一个简单的短期记忆模块，用于存储智能体的行动与反思轨迹
    """
    def __init__(self):
        """
        初始化一个空列表来存储所有记录
        """
        self.records: List[Dict[str, Any]] = []

    def add_record(self, record_type: str, content: str):
        """
        向记忆中添加一条新纪录

        Args:
            record_type (str): 记录的类型('execution' 或 'reflection')
            content (str): 记录的具体内容(例如，生成的代码或反思的反馈)
        """
        record = {"type": record_type, "content": content}
        self.records.append(record)
        print(f"📝 记忆已更新，新增一条 '{record_type}' 记录。")

    def get_trajectory(self) -> str:
        """
        将所有记忆记录格式化为一个连贯的字符串文本，用于构建提示词
        """
        trajectory_parts = []
        for record in self.records:
            if record["type"] == "execution":
                trajectory_parts.append(f"--- 上一轮尝试 (代码) ---\n{record['content']}")
            elif record["type"] == "reflection":
                trajectory_parts.append(f"--- 评审员反馈 ---\n{record['content']}")
        
        return "\n\n".join(trajectory_parts)

    def get_last_execution(self) -> Optional[str]:
        """
        获取最近一次的执行结果 (例如，最新生成的代码)。
        如果不存在，则返回 None。
        """
        for record in reversed(self.records):
            if record["type"] == "execution":
                return record["content"]
        
        return None




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
