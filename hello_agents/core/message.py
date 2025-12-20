# -*- coding: utf-8 -*-

# ***************************************************
# * File        : message.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-18
# * Version     : 1.0.121822
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
from typing import Optional, Dict, Any, Literal
from datetime import datetime

from pydantic import BaseModel

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


# 定义消息角色的类型，限制其取值
MessageRole = Literal["user", "assistant", "system", "tool"]


class Message(BaseModel):
    """
    消息类
    """

    content: str
    role: MessageRole
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None

    def __init__(self, content: str, role: MessageRole, **kwargs):
        super().__init__(
            content=content,
            role=role,
            timestamp=kwargs.get("timestamp", datetime.now()),
            metadata=kwargs.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式（OpenAI API 格式）
        """
        return {
            "role": self.role,
            "content": self.content,
        }
    
    def __str__(self) -> str:
        return f"[{self.role}] {self.content}"




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
