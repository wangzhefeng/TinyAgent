# -*- coding: utf-8 -*-

# ***************************************************
# * File        : run_all.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 模式实验室总入口 —— 顺序跑通六个模式
# ***************************************************

# python libraries

# third-party libraries
from tinyagent import OpenAIChatModel

# local libraries
from learn.level4_patterns import (
    chaining,
    evaluator_optimizer,
    routing_pattern,
    self_correction,
    supervisor,
    swarm_handoff,
)


def main():
    model = OpenAIChatModel()
    chaining.run(model)
    routing_pattern.run(model)
    self_correction.run(model)
    evaluator_optimizer.run(model)
    supervisor.run(model)
    swarm_handoff.run(model)


if __name__ == "__main__":
    main()
