# -*- coding: utf-8 -*-

"""
消息系统
"""

# python libraries
from typing import Optional, Dict, Any, Literal
from datetime import datetime

from pydantic import BaseModel


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
    print(Message(content="Hello, world!", role="user").content)
    print(Message(content="Hello, world!", role="user").role)
    print(Message(content="Hello, world!", role="user").timestamp)
    print(Message(content="Hello, world!", role="user").metadata)
    
    msg = Message(content="Hello, world!", role="user")
    print(msg)
    print(msg.content)
    print(msg.role)
    print(msg.timestamp)
    print(msg.metadata)
    
    msg = msg.to_dict()
    print(msg)

if __name__ == "__main__":
    main()
