"""Quickstart: ready-made orchestration agents (generate-critique-refine, plan-execute)."""

from tinyagent import OpenAIChatModel, PlanAndSolveAgent, ReflectionAgent


def main():
    model = OpenAIChatModel()  # config from .env (LLM_* variables)

    print("=== ReflectionAgent: generate -> critique -> refine ===")
    code = ReflectionAgent(model, max_iterations=1).run(
        "编写一个函数，找出 100 以内所有的素数"
    )
    print(code[:400], "...\n")

    print("=== PlanAndSolveAgent: plan -> stepwise execution ===")
    answer = PlanAndSolveAgent(model).run("用三步说明如何选一个时序预测基线模型。")
    print(answer[:400])


if __name__ == "__main__":
    main()
