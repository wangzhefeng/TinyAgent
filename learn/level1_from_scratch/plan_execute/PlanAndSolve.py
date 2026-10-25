# -*- coding: utf-8 -*-

# ***************************************************
# * File        : PlanAndSolve.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : Plan-and-Execute 范式入口（M1 独立化，python -m 运行）
# ***************************************************

# python libraries

# local libraries
from learn.level0_llm_basics.llm_client import ChatClient
from learn.level1_from_scratch.plan_execute.executor import Executor
from learn.level1_from_scratch.plan_execute.planner import Planner


class PlanAndSolveAgent:
    def __init__(self, llm_client: ChatClient):
        """
        初始化智能体，同时创建规划器和执行器实例
        """
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)

    def run(self, question: str):
        """
        运行智能体的完整流程：先规划，后执行
        """
        print(f"\n--- 开始处理问题 ---\n问题: {question}")

        # 1. 调用规划器生成计划
        plan = self.planner.plan(question)

        # 检查计划是否成功生成
        if not plan:
            print("\n--- 任务终止 --- \n无法生成有效的行动计划。")
            return None

        # 2. 调用执行器执行计划
        final_answer = self.executor.execute(question, plan)
        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")
        return final_answer


# 测试代码 main 函数
def main():
    agent = PlanAndSolveAgent(llm_client=ChatClient())
    agent.run("如何系统地学习时间序列预测？请给出可操作的学习计划。")


if __name__ == "__main__":
    main()
