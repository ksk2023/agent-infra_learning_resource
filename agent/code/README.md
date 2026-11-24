# 离线实验导航

这些实验只依赖 Python 标准库，不需要模型 API、GPU、向量数据库或网络。它们用于隔离验证 Agent 系统的控制机制，不用于证明真实模型的推理能力。

## 运行方式

在 `agent/` 根目录执行：

```bash
python code/ch02/structured_output.py
python code/ch03/mini_agent.py
python code/ch05/dag_planner.py
python code/ch06/memory_context.py
python code/ch07/rag_lab.py
python code/ch08/checkpoint_runner.py
python code/ch12/eval_metrics.py
python code/ch13/trace_metrics.py
python code/ch14/policy_gate.py
python -m unittest discover -s tests -v
python scripts/validate.py
```

Windows 可使用同样的 `python` 命令。如果系统 Python 不在 PATH，请激活你为项目创建的虚拟环境。本目录实验没有第三方依赖。

## 实验地图

| 实验 | 覆盖机制 | 重点观察 | 明确边界 |
|---|---|---|---|
| `ch02/structured_output.py` | 严格 JSON 动作协议 | 合法 `tool_call`/`final`；围栏、缺字段和额外字段被拒绝 | 不评价模型生成 JSON 的能力 |
| `ch03/mini_agent.py` | ReAct 式循环、工具注册表、观察回传、最大步数 | 工具结果进入上下文；未知工具成为结构化观察；循环可终止 | 模型是脚本化测试替身；计算器不是任意代码执行器 |
| `ch05/dag_planner.py` | DAG 校验、环检测、按层拓扑排序 | 同层节点可并行是调度提示，不代表脚本已并行执行 | 不包含真实任务队列与故障调度 |
| `ch06/memory_context.py` | 记忆作用域、过期、相关性排序、字符预算 | 跨用户记忆不可见；过期记忆不召回；低优先级内容被省略 | 词项匹配不是语义检索；字符数不是模型 token 数 |
| `ch07/rag_lab.py` | 标准库 TF-IDF、引用存在性、Recall@k | 不存在的引用被识别；检索分数可比较但不等于事实置信度 | 引用存在不代表引用支持结论；不含真实 embedding 服务 |
| `ch08/checkpoint_runner.py` | 原子 JSON checkpoint、resume、幂等键 | 故障后跳过已完成步骤；重复 `operation_id` 不新增副作用 | 临时目录会清理；真实系统还需处理崩溃窗口、存储一致性和对账 |
| `ch12/eval_metrics.py` | 单次成功率、`pass@k`、`pass^k`、无效样本与安全分类 | `invalid` 不混入 Agent 失败；安全违规不计为干净成功 | 概率公式假设独立同分布，不替代真实重复试验 |
| `ch13/trace_metrics.py` | 成功率、nearest-rank 分位数、调用量、工具错误和成本 | 失败重试也消耗成本；只有满足质量且无违规的完成项进入成功分母 | 教学聚合器不是完整遥测、计费或 SLO 系统 |
| `ch14/policy_gate.py` | 模型外策略门、资源 scope、高风险审批、参数哈希 | 未知工具、跨资源访问、审批后改参和伪造 `approved` 均被拒绝 | 只执行策略判定；不是完整 IAM、沙箱或真实审批系统 |

## 建议练习顺序

1. 先预测输出，再运行脚本并保存原始结果。
2. 阅读实现，为每个公开函数补一个正常、边界和失败用例。
3. 一次只修改一个机制，例如把最大步数从 6 改为 1，观察失败类型。
4. 把结果填入 `templates/experiment-report.md`，写清样本、命令、限制和未验证部分。
5. 接入真实模型或服务时新建适配器，不修改这些可重复的离线基线。

## 接入真实能力时的最低要求

- 固定模型提供方、模型标识、提示词、采样参数、工具 schema、依赖和环境快照。
- 先接只读、假数据工具；写操作要有资源级授权、幂等、审批和审计。
- 密钥通过环境变量或密钥管理工具提供，不写入源码、trace 或提交到 Git。
- 真实模型的结果必须与离线控制逻辑测试分开报告。
- 任何真实 benchmark 分数都绑定任务版本、harness、运行日期和原始轨迹。
