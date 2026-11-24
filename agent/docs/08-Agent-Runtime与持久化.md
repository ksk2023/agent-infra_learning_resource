# 第 08 章：Agent Runtime 与持久化

## 本章导学

长任务会跨多次模型调用、工具执行、人工等待和进程重启。运行时若只把历史放在内存里，就无法可靠恢复；若简单从头重放，又可能重复发邮件或扣款。本章学习 checkpoint、事件、幂等与人工中断。

## 学习目标

- 区分会话状态、事件日志、artifact 与外部业务状态。
- 设计可恢复执行的 checkpoint 边界。
- 理解 replay、resume 和副作用幂等的关系。
- 实现取消、等待人工和失败恢复的基本语义。

## 1. Runtime 管什么

```text
Run：一次任务实例及其预算、身份和最终状态
Thread/Session：跨 run 的会话连续性
Step/Node：可恢复的模型、工具或确定性计算单元
Event：状态迁移、调用、错误、审批等事实
Artifact：报告、文件、截图、补丁等受控产物
Checkpoint：某一边界上足以继续运行的状态快照
```

上下文是模型看到的视图；运行时状态是系统恢复所需的事实。两者不必完全相同，完整文档和大型 artifact 通常放在外部受控存储，checkpoint 只保留引用。

## 2. 状态机优先于隐式控制

建议显式建模：

```text
created -> running
running -> waiting_tool / waiting_approval / completed
running -> failed_retryable / failed_final / cancelled
waiting_approval -> running / rejected / cancelled
failed_retryable -> running（受重试预算约束）
```

每次迁移要有触发事件、时间和操作者。模型可建议动作，但只有运行时能改变运行状态。等待审批时 run 不应被标记为完成。

## 3. Checkpoint 边界怎么选

优先在以下位置保存：

- 收到并规范化任务后。
- 模型产生结构化动作、但尚未执行副作用前。
- 工具成功提交并确认结果后。
- 计划状态迁移后。
- 进入人工等待、取消或最终状态前。

保存过于稀疏会重复工作；过于频繁会增加延迟和存储。需要测量恢复点目标与 checkpoint 开销，而不是盲目“每 token 都落盘”。

## 4. Resume 不等于从头 Replay

```text
从头 replay：再次执行所有步骤
  优点：可重建状态
  风险：模型结果漂移、工具副作用重复、成本高

从 checkpoint resume：读取已确认状态，只执行未完成步骤
  优点：减少重复工作
  要求：快照完整、版本兼容、外部状态可核对
```

对“请求已发出但响应丢失”的工具，恢复时应先按 `call_id` 或幂等键查询，而非直接重试。纯计算步骤可缓存结果；有副作用步骤需要唯一操作记录。

## 5. 人工中断是持久状态

一个可靠审批流程：

1. 运行时保存待执行工具、规范化参数、风险、身份和状态差异预览。
2. checkpoint 后进入 `waiting_approval`，释放不必要资源。
3. 审批人看到具体动作而非“Agent 想做一件事”。
4. 批准后重新检查权限、参数版本和资源状态，再执行。
5. 拒绝、修改、超时和撤销都有独立事件与结果。

审批界面不能直接执行模型后来替换的参数；批准对象应与参数哈希或版本绑定。

## 6. 最低实践：注入故障并恢复

运行：

```bash
python code/ch08/checkpoint_runner.py
```

脚本在临时目录中保存步骤结果，并演示故障后的恢复。完成：

1. 第一次运行在指定步骤前失败，记录 checkpoint。
2. 第二次恢复，验证已完成纯计算步骤不重复执行。
3. 为一个模拟写工具添加 `operation_id`，验证重复恢复不会重复追加副作用。
4. 删除一个 artifact 后恢复，观察哪些状态检查能发现问题。
5. 增加 `waiting_approval` 状态，并说明批准后需要重新校验什么。

### 验收标准

报告能区分“进程恢复”“模型历史恢复”和“外部业务状态已提交”；不能只用最终文本判断是否恢复成功。

## 7. 源码任务

阅读 LangGraph 或另一个持久化运行时，跟踪：

```text
状态定义 -> 节点调度 -> checkpoint 写入
  -> interrupt -> 持久化等待 -> resume -> 节点结果合并
```

重点看版本升级、并行节点部分成功、任务取消和存储故障如何处理，而不只读 quickstart。

## 8. 本章自测

1. 保存完整聊天记录是否足以从故障中恢复？
2. 为什么从 checkpoint 恢复前仍需检查外部业务状态？
3. 审批通过后，为什么不应允许模型无审计地替换参数？
4. checkpoint 越频繁是否一定越可靠？

<details><summary>参考思路</summary>

1. 不足，还需计划、工具调用、预算、身份、artifact、外部环境状态和版本信息。
2. 故障可能发生在工具提交之后，需避免重复副作用并确认真实进度。
3. 审批绑定的是具体动作；替换参数等于新动作，应重新校验和审批。
4. 不一定，频率增加开销和故障点；可靠性还取决于原子性、完整性和恢复测试。
</details>

## 9. 推荐资源

- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)：durable execution、streaming、human-in-the-loop 和 persistence。
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)：checkpoint 与 store 的边界。
- [Temporal Documentation](https://docs.temporal.io/)：通用持久化工作流、重试与确定性执行概念，可用于对照 Agent Runtime。

上一章：[RAG 与证据驱动回答](07-RAG与证据驱动回答.md)｜下一章：[MCP、A2A 与能力互操作](09-MCP-A2A与能力互操作.md)
