# 第 10 章：多 Agent 协作与编排

## 本章导学

多 Agent 的价值来自职责、上下文、权限或执行环境的合理拆分，而不是让多个角色互相称赞。本章比较常见编排模式，并要求所有多 Agent 结论都与单 Agent 基线对照。

## 学习目标

- 识别适合拆分与不适合拆分的任务。
- 区分 sequential、router、manager、handoff 和 orchestrator-workers。
- 设计跨 Agent 的输入输出、状态、预算和终止契约。
- 测量协作收益、协调开销与错误传播。

## 1. 何时拆分

合理动机：

- **上下文隔离**：子任务需要大量检索，但主 Agent 只需要结论和证据。
- **权限隔离**：浏览不可信网页的执行单元不能直接接触付款工具。
- **专业化**：不同子任务需要不同工具、prompt、模型或评测。
- **并行与吞吐**：独立子任务可同时运行，缩短关键路径。
- **所有权与部署**：不同团队维护独立 Agent，通过稳定协议协作。

不合理动机：任务本身很简单、只是想让界面出现更多角色、没有单 Agent 基线、无法定义子任务验收。

## 2. 常见模式

| 模式 | 控制方式 | 适用 | 主要风险 |
|---|---|---|---|
| Sequential | 固定顺序传递 artifact | 研究→写作→审阅 | 上游错误固化、串行延迟 |
| Router | 分类后交给一个专家 | 客服意图、工具域路由 | 误分类、路由边界不清 |
| Manager / Agent-as-tool | 主 Agent 调用专家并保留控制 | 主任务需要临时专业能力 | 调用成本、结果过度压缩 |
| Handoff | 将当前交互控制转交专家 | 专人接管完整会话 | 状态/权限意外继承、责任不清 |
| Orchestrator-Workers | 动态拆解并汇总多个 worker | 子任务事先难穷举 | 计划漂移、重复劳动、协调膨胀 |

这些模式可与确定性图组合。关键不是名称，而是：谁有控制权、谁保存状态、谁验证结果、谁拥有最终审批权。

## 3. 子任务契约

每次委派至少包含：

```text
task_id / parent_run_id
目标、范围、非目标
输入 artifact 及版本/来源
允许工具、身份、数据作用域
输出 schema 与验收条件
最大步数、token、费用、时间和递归深度
取消、超时、失败与升级路径
```

输出应包含证据和状态，而不是只有“已完成”。主 Agent 需要能区分未执行、部分完成、工具失败和验收失败。

## 4. 共享状态与上下文

- 默认传递最小必要上下文，而不是所有 Agent 共享完整消息流。
- 用受控 artifact 传递长报告、搜索结果和代码补丁，保留引用与版本。
- 明确共享状态的写入者和冲突策略；数据库事务、文件锁或分区优于“大家注意不要冲突”。
- 子 Agent 不应继承父 Agent 的全部凭据；按任务重新授权。
- 对循环委派设置深度和总预算，避免 A 调 B、B 再调 A 无限递归。

## 5. 多 Agent 不是独立评委的替代品

多个由相同模型、相同提示和相同错误证据驱动的 Agent，可能产生相关错误。投票数量增加不自动带来独立性。

若使用 reviewer/critic：

- 给它可验证的检查工具或独立证据。
- 明确哪些问题是阻断项，哪些只是风格建议。
- 测量 reviewer 的误报与漏报，不默认它永远正确。
- 对同一输出重复修审设置上限，并保留每版差异。

## 6. 最低实践：先做对照设计，再写编排

为“生成带来源的技术调研报告”设计两个实现：

```text
A：单 Agent，依次检索、阅读、写作、引用检查
B：Researcher 产生证据包，Writer 生成报告，Verifier 检查引用
```

要求：

1. 两个实现使用相同模型、工具、任务集和总预算口径。
2. Researcher 输出固定 evidence schema，Writer 不得伪造未见来源。
3. Verifier 至少用代码检查引用存在性和文档定位。
4. 比较任务成功率、引用支持率、token、P95 延迟、单位成功成本。
5. 找出一个 B 更差的情景，例如简单问题或 reviewer 误判。

### 验收标准

若不能证明 B 在明确指标上有净收益，就保留更简单的 A。架构图不能替代实验。

## 7. 源码任务

选择一个框架，分别追踪 manager 调用与 handoff：

- 子 Agent 收到哪些消息和工具？
- 会话状态由谁持有，何时回到父 Agent？
- guardrail 在交接边界是否仍然生效？
- 子 Agent 失败、取消和超时如何传播？
- 是否支持 checkpoint 和人工中断？

## 8. 本章自测

1. 为什么三个角色投票不一定比单个 reviewer 更可靠？
2. Manager 与 Handoff 的控制权差异是什么？
3. 为什么子 Agent 不应默认继承父 Agent 全部权限？
4. 多 Agent 成功率提高但成本翻倍，如何判断是否值得？

<details><summary>参考思路</summary>

1. 它们可能共享模型、提示和证据偏差，错误相关；需要独立证据和评审质量测量。
2. Manager 保留主控制并调用专家；Handoff 将当前交互控制转交给接收者。
3. 子任务通常只需更小权限，继承会扩大越权和注入影响范围。
4. 结合业务价值、延迟、风险和单位成功成本，在同预算/质量约束下比较，不能只看成功率。
</details>

## 9. 推荐资源

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)：agents-as-tools、handoffs、guardrails 与 tracing。
- [Google ADK: Agents](https://google.github.io/adk-docs/agents/) 与 [Workflows](https://google.github.io/adk-docs/agents/multi-agents/)：从单 Agent 到图、动态与协作式 workflow。
- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)：以显式状态和图组合确定性与 Agent 步骤。

上一章：[MCP、A2A 与能力互操作](09-MCP-A2A与能力互操作.md)｜下一章：[Agentic RL 与持续改进](11-Agentic-RL与持续改进.md)
