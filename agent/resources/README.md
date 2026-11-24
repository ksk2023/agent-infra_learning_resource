# 参考资料与扩展资源图谱

本页回答两件事：**本教程主要参考了什么**，以及**学到某一机制后去哪里核对原始资料**。正文与离线代码独立编写；中文课程用于参考学习组织与主题覆盖，官方文档和论文用于核对机制，不复制其章节或代码。

## 1. 本教程直接参考的主干资料

| 资料 | 主要参考内容 | 对应章节 |
|---|---|---|
| [Datawhale Agent-Learning-Hub](https://github.com/datawhalechina/Agent-Learning-Hub) | 中文 Agent 学习路线、阶段划分与资源导航方式 | 00、01、15 |
| [Datawhale Hello-Agents](https://github.com/datawhalechina/hello-agents) | 中文智能体课程的主题覆盖与理论—实践结合方式 | 全课程组织参考 |
| [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents) | workflow/Agent 区分、渐进复杂度、routing、orchestrator-workers 等模式 | 01、05、10 |
| [OpenAI: A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) | 模型、工具、指令、编排与 guardrail 的系统视角 | 01–04、10、14 |
| [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) | Runner、工具、sessions、handoffs、guardrails 与 tracing 的工程映射 | 02–04、08–10、13 |
| [ReAct](https://arxiv.org/abs/2210.03629) | reasoning 与 acting 交错、环境反馈闭环 | 03 |
| [Toolformer](https://arxiv.org/abs/2302.04761) | 模型学习 API 调用、参数与结果吸收的训练视角 | 04、11 |
| [Reflexion](https://arxiv.org/abs/2303.11366) | 语言反馈、episodic memory 与跨尝试改进 | 05、06 |
| [Generative Agents](https://arxiv.org/abs/2304.03442) | 记忆流、检索、反思和规划的组合及消融 | 06 |
| [RAG 原始论文](https://arxiv.org/abs/2005.11401) | 参数记忆与非参数记忆结合的基础概念 | 07 |
| [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | checkpoint、thread 与跨 thread store 的边界 | 06、08 |
| [MCP 官方架构与规范](https://modelcontextprotocol.io/docs/learn/architecture) | Host/Client/Server、工具/资源/提示和信任边界 | 04、09、14 |
| [A2A 官方文档](https://a2a-protocol.org/latest/) | Agent 间能力发现、任务与消息协作的协议视角 | 09、10 |
| [AgentBench](https://arxiv.org/abs/2308.03688)、[GAIA](https://arxiv.org/abs/2311.12983)、[SWE-bench](https://www.swebench.com/SWE-bench/) | 多环境、通用助手和软件工程任务的结果评测 | 12 |
| [WebArena](https://github.com/web-arena-x/webarena)、[OSWorld](https://arxiv.org/abs/2404.07972) | 可复现 Web/操作系统环境与状态验证 | 12 |
| [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) | 工具、权限、记忆、注入、多 Agent 与供应链控制 | 09、14 |
| [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) | 治理、测量和风险管理的通用框架 | 12–14 |

以上资料不是要求一次读完的书单。先按当前章节选一个主干来源，再用实现或小实验核对。

## 2. 官方指南与学习路径

- [OpenAI Building agents](https://developers.openai.com/tracks/building-agents)：从模型、工具到编排和 guardrail 的官方路径。
- [OpenAI Agents SDK: Agents](https://openai.github.io/openai-agents-python/agents/) 与 [Tools](https://openai.github.io/openai-agents-python/tools/)：核对结构化输出、工具 schema、执行管线和模型设置。
- [OpenAI Agents SDK: Tracing](https://openai.github.io/openai-agents-python/tracing/)：查看一次 run 内 model、tool、handoff 与 guardrail 的遥测关系。
- [Google ADK Technical Overview](https://google.github.io/adk-docs/get-started/about/)：Agent、Tool、Session、State、Artifact 的概念划分。
- [microsoft/ai-agents-for-beginners](https://github.com/microsoft/ai-agents-for-beginners)：入门主题索引；代码示例应回到对应 SDK 官方文档核对。
- [Lilian Weng: LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)：规划、记忆与工具使用的经典综述，适合作为概念地图而非最新 API 依据。

## 3. 核心论文：从机制到实验

| 论文 | 阅读重点 | 不要直接推出什么 |
|---|---|---|
| [ReAct](https://arxiv.org/abs/2210.03629) / [项目页](https://react-lm.github.io/) | 推理轨迹与动作/观察如何交错 | 不能推出任意业务工具调用都可靠 |
| [Toolformer](https://arxiv.org/abs/2302.04761) | 何时调用 API、如何传参、怎样利用结果 | 不等于现代 SDK 的工具协议规范 |
| [Reflexion](https://arxiv.org/abs/2303.11366) | 外部评价、语言反馈、记忆与消融 | 自我评价不等于真实正确性 |
| [Generative Agents](https://arxiv.org/abs/2304.03442) | 记忆检索、反思、规划与行为的关系 | 不等于所有应用都需要长期人格记忆 |
| [Voyager](https://arxiv.org/abs/2305.16291) | 自动课程、技能库、执行反馈与验证 | 特定环境收益不能直接迁移到生产 Agent |
| [RAG](https://arxiv.org/abs/2005.11401) | 参数/非参数知识结合的经典建模思路 | 现代 RAG 的检索和引用问题并未因此自动解决 |

读论文时记录任务、环境、基线、消融、评价器和失败案例；不要只摘架构图。

## 4. 框架与多 Agent 编排

- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)：显式状态图、durable execution、人工中断和持久化。
- [Google ADK: Agents](https://google.github.io/adk-docs/agents/) 与 [Multi-agent Workflows](https://google.github.io/adk-docs/agents/multi-agents/)：静态 workflow、动态转移和协作模式对照。
- [Hugging Face smolagents](https://github.com/huggingface/smolagents)：轻量 Agent 与 CodeAgent，可用于追踪最小循环和代码执行边界。
- [NirDiamant/GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents)：按模式寻找示例的索引，不应替代原始论文与官方文档。

建议围绕一个行为读源码，例如“工具超时如何进入轨迹”或“interrupt 后如何 resume”，固定 commit 并使用 `templates/source-reading.md`。

## 5. Runtime、持久化与互操作

- [Temporal Documentation](https://docs.temporal.io/)：持久化工作流、重试、确定性和副作用边界，可与 Agent Runtime 对照。
- [MCP Specification](https://modelcontextprotocol.io/specification/latest)：当前协议原语、生命周期、传输与版本的权威入口。
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/latest/basic/security_best_practices)：混淆代理、token、会话与协议安全问题。
- [A2A Specification 与 SDK 仓库](https://github.com/a2aproject/A2A)：规范、SDK 和示例；实际对接以当前规范为准。
- [OpenAI Agents SDK: MCP](https://openai.github.io/openai-agents-python/mcp/)：一种 Agent SDK 的 MCP 接入与工具生命周期示例。

协议连接不等于权限授予。每个 Server、Agent、Skill 和工具描述都应经过来源审查、schema 校验、资源授权和审计。

## 6. RAG、记忆与上下文

- [LlamaIndex](https://github.com/run-llama/llama_index)：数据接入、索引、检索与 Agent 生态入口。
- [RAGFlow](https://github.com/infiniflow/ragflow)：文档理解、分块和 RAG 工程实现对照。
- [Letta](https://github.com/letta-ai/letta)：状态化 Agent 与记忆层设计。
- [mem0](https://github.com/mem0ai/mem0)：长期记忆抽取、存储和检索的一种实现入口。

比较时重点看写入审查、来源、作用域、过期/删除、冲突处理和评测，而非只看“支持长期记忆”。接入前分别核对当前架构、数据去向和许可证。

## 7. Coding、Browser 与 Computer-use

- [SWE-bench 官方入口](https://www.swebench.com/SWE-bench/)：真实 GitHub issue、代码环境和可执行测试验证。
- [WebArena](https://github.com/web-arena-x/webarena)：自托管网站任务与可复现状态检查。
- [OSWorld](https://arxiv.org/abs/2404.07972)：真实操作系统/应用中的多模态任务与环境初始化。
- [Voyager](https://arxiv.org/abs/2305.16291)：开放环境技能获取与执行反馈的研究案例。

这类实验先用隔离环境、快照和假账号；不要把无限制 shell、个人浏览器主会话、生产凭据和真实支付混在第一次实验中。

## 8. 评测与 Benchmark

- [AgentBench](https://arxiv.org/abs/2308.03688)：多类交互环境的横向能力与失败分析。
- [GAIA](https://arxiv.org/abs/2311.12983)：通用助手、工具与浏览任务。
- [SWE-bench](https://www.swebench.com/SWE-bench/)：软件工程结果的可执行验证。
- [WebArena](https://github.com/web-arena-x/webarena)：Web 任务及环境状态验证。
- [OSWorld](https://arxiv.org/abs/2404.07972)：操作系统任务、环境控制和可执行评价。
- [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench)：工具—Agent—用户动态交互与政策约束。

使用任何榜单前，核对数据版本、子集、harness、工具、模型、采样参数、运行日期和评分器。不要把不同版本数字拼成自己的排名，也不要用公共分数替代私有业务与安全任务集。

## 9. 可观测性与可靠性

- [OpenTelemetry: GenAI Observability](https://opentelemetry.io/blog/2026/genai-observability/)：GenAI 与 Agent 遥测示例；语义约定可能演进，以当前规范为准。
- [Prometheus](https://github.com/prometheus/prometheus)：指标采集与告警生态。
- [Grafana](https://github.com/grafana/grafana)：指标、日志与 trace 面板入口。
- [Temporal Documentation](https://docs.temporal.io/)：用通用持久化执行概念检验重试、恢复与副作用假设。

日志和 trace 默认最小化敏感信息，不以完整 prompt、秘密或个人信息作为常规标签。

## 10. 安全、治理与人机协同

- [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)：Agent 专项分层控制清单。
- [OWASP LLM01: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)：直接与间接提示注入的风险和缓解。
- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)：Govern、Map、Measure、Manage 的风险管理框架。
- [NIST Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)：生成式 AI 风险画像与治理参考。
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/latest/basic/security_best_practices)：协议特有的安全边界。

安全结论应来自模型之外的策略执行、隔离、审批与对抗回归，不以系统提示词或模型自我声明代替。

## 11. Agentic RL 与训练系统

- [Datawhale Agentic-RL-Lab](https://github.com/datawhalechina/agentic-rl-lab)：中文 Agentic RL 论文复现和实验导航。
- [Hugging Face TRL](https://github.com/huggingface/trl)：后训练与 RL 接口。
- [verl](https://github.com/verl-project/verl)：分布式后训练、rollout 与训练系统。
- [OpenRLHF](https://github.com/OpenRLHF/OpenRLHF)：基于 Ray 等组件的 RLHF/训练系统实现对照。

进入训练前先确认任务环境、工具协议、可验证奖励、轨迹数据和纯系统基线已经可靠。模拟工具上的控制测试不等于训练收益。

## 12. 中文社区与基础补给

- [Datawhale Agent-Learning-Hub](https://github.com/datawhalechina/Agent-Learning-Hub)：持续发现中文 Agent 课程、论文和实践项目。
- [Datawhale Hello-Agents](https://github.com/datawhalechina/hello-agents)：中文智能体系统教程。
- [Datawhale Happy-LLM](https://github.com/datawhalechina/happy-llm)：补充大模型原理。
- [Datawhale Agentic-RL-Lab](https://github.com/datawhalechina/agentic-rl-lab)：补充 Agentic RL 训练与复现。
- [CS 自学指南](https://github.com/PKUFlyingPig/cs-self-learning)：补充数据结构、系统与软件工程基础。

## 13. 如何使用扩展资料

优先级建议：

```text
当前要解决的问题 -> 官方规范/文档 -> 原始论文与测试
-> 真实源码固定版本 -> 社区教程与二手总结
```

- **查 API/协议**：以当前官方文档和规范为准，记录访问日期与版本。
- **查机制结论**：读原论文的任务、基线、消融和限制，不把特定环境结果泛化。
- **读框架**：固定 tag/commit，同时读实现和测试，完成一个最小行为实验。
- **用代码/数据/模型/文档**：分别核对许可证、引用要求、隐私和使用限制；开源可见不等于可任意复制。
- **看榜单**：保存自己的原始轨迹与配置，不混用不同 harness 或任务版本的数字。
- **发现链接或 API 变化**：回到项目官方导航定位最新版本，不凭记忆补写新接口。
