"""Quickstart: long-term memory with adaptive retrieval (ADR-0007)."""

from tinyagent import FileLongTermMemory


def main():
    memory = FileLongTermMemory()  # defaults to logs/tinyagent/memory.jsonl

    memory.add("用户是时序方向的算法工程师，重视口径严谨与数据准确性")
    memory.add("项目默认走智谱 OpenAI 兼容端点，模型阶梯见 .env")
    memory.add("回测口径必须一致才能比较两个模型")

    # 有 API key 时走 embedding 余弦检索；离线自动退化为关键词匹配
    for hit in memory.retrieve("这个用户的职业背景是什么？", k=2):
        print(f"[memory] {hit['text']}")


if __name__ == "__main__":
    main()
