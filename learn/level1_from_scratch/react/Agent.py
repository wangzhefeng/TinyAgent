# -*- coding: utf-8 -*-

# ***************************************************
# * File        : Agent.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : 手写 ReAct Agent（M1 API 化：模型后端注入，工具统一分发）
# ***************************************************

# python libraries
from typing import List

# third-party libraries
import json5

# local libraries
from learn.level1_from_scratch.react.tool import Tools

TOOL_DESC = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model} Parameters: {parameters} Format the arguments as a JSON object."""
REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Rules (MUST follow):
1. The Observation line is filled in ONLY by the system after the Action is executed. NEVER write, guess, or imagine any Observation content yourself.
2. Before calling a tool that needs a path (e.g. read_config / read_result_summary), you MUST first call the corresponding list tool (list_configs / list_results) and use a REAL path from its result. NEVER guess or invent file paths.
3. If an Observation reports an error (unknown tool, file not found, failure), adapt your next Action to fix it (e.g. call the list tool first). NEVER pretend the call succeeded or fabricate its result.
4. Your Final Answer must be based strictly on the Observation contents actually returned by the system.

Begin!
"""


class Agent:
    """
    Agent 的结构是一个 React 的结构，提供一个 `system_prompt`，
    使得 LLM 知道自己可以调用哪些工具，并以什么样的格式输出。

    M1 改造：模型后端通过依赖注入（`model` 参数），API 后端用
    `learn.level0_llm_basics.llm_client.ChatClient`，本地推理后端用
    `learn.level1_from_scratch.react.llm_local.InternLM2Chat`（可选，
    需 torch/transformers）；两者共用同一 `chat` 接口。
    工具通过 `tools` 参数注入（默认 ReAct 演示工具集），需提供
    `toolConfig`（描述）与 `call(name, **kwargs)`（分发）。

    每次用户的提问，如要需要调用工具的话，都会进行两次的 LLM 调用：
        - 第一次解析用户的提问，选择调用的工具和参数；
        - 第二次将工具返回的结果与用户的提问整合，这样就可以实现一个 ReAct 的结构。
    """

    def __init__(self, model, tools=None) -> None:
        # 工具
        self.tool = tools if tools is not None else Tools()
        # system prompt
        self.system_prompt = self._build_system_input()
        # 模型后端（API 或本地）
        self.model = model

    def _build_system_input(self):
        """
        构建 ReAct 形式的 system prompt
        该 system prompt 告诉 LLM，可以调用哪些工具，
        以什么样的方式输出，以及工具的描述信息和工具应该接受什么样的参数。
        """
        tool_descs = [TOOL_DESC.format(**tool) for tool in self.tool.toolConfig]
        tool_names = [tool["name_for_model"] for tool in self.tool.toolConfig]
        tool_descs = "\n\n".join(tool_descs)
        tool_names = ",".join(tool_names)
        sys_prompt = REACT_PROMPT.format(tool_descs=tool_descs, tool_names=tool_names)

        return sys_prompt

    def _parse_latest_plugin_call(self, text: str):
        """
        从模型输出中解析最近一次 Action / Action Input，
        并补全缺失的 Observation 分隔符。
        """
        plugin_name, plugin_args = "", ""

        i = text.rfind("\nAction:")
        j = text.rfind("\nAction Input:")
        k = text.rfind("\nObservation:")
        if 0 <= i < j:  # if the text has "Action" and "Action input"
            if k < j:  # but does not contain "Observation"
                text = text.rstrip() + "\nObservation:"  # add it back
            k = text.rfind("\nObservation:")
            # 修复课程代码的切片 bug：从 "\nAction:" 之后取工具名（原版少切冒号，
            # 会把工具名解析成 ": list_configs" 导致"未知工具"）
            plugin_name = text[(i + len("\nAction:")):j].strip()
            plugin_args = text[(j + len("\nAction Input:")):k].strip()
            text = text[:k]

        return plugin_name, plugin_args, text

    def _call_plugin(self, plugin_name, plugin_args):
        """
        分发工具调用（json5 宽松解析参数），返回 Observation 文本。
        """
        plugin_args = json5.loads(plugin_args)
        return "\nObservation:" + str(self.tool.call(plugin_name, **plugin_args))

    def text_completion(self, text: str, history: List = [], max_tool_rounds: int = 5):
        """
        调用 LLM，按 ReAct 逻辑迭代调用工具直至给出 Final Answer
        （M1 升级：课程版固定两次调用，改为有界循环——每轮解析 Action →
        执行工具 → 回填 Observation → 再生成；无工具调用或达到轮数上限即止）。

        Args:
            text (_type_): 用户的提问
            history (list, optional): 消息历史. Defaults to [].
            max_tool_rounds (int, optional): 最大工具调用轮数. Defaults to 5.

        Returns:
            tuple: (最终回复, 更新后的消息历史)
        """
        # query
        text = f"\nQuestion: {text}"
        # 模型生成
        response, history = self.model.chat(
            prompt=text,
            history=history,
            meta_instruction=self.system_prompt,
        )
        # ReAct 迭代循环
        for _ in range(max_tool_rounds):
            plugin_name, plugin_args, response = self._parse_latest_plugin_call(response)
            if not plugin_name:
                break  # 无工具调用：已是 Final Answer
            response += self._call_plugin(plugin_name, plugin_args)
            response, history = self.model.chat(
                prompt=response,
                history=history,
                meta_instruction=self.system_prompt,
            )

        return response, history


# 测试代码 main 函数
def main():
    from learn.level0_llm_basics.llm_client import ChatClient

    agent = Agent(model=ChatClient())
    print(agent.system_prompt)

    response, history = agent.text_completion(text="你好", history=[])
    print(response)

    response, history = agent.text_completion(
        text="计算 (123 + 456) * 2 等于多少？", history=history
    )
    print(response)


if __name__ == "__main__":
    main()
