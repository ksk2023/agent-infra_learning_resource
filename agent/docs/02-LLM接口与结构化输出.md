# 第 02 章：LLM 接口与结构化输出

## 本章导学

Agent Loop 的输入和输出不能靠“大概能解析”的字符串维持。本章把模型调用拆成明确接口：消息、指令、工具描述、动作、错误和用量，并用结构化输出建立控制边界。

## 学习目标

- 说明 messages、instructions、tools 和 response 的职责。
- 设计可校验的动作 schema，区分工具调用与最终回答。
- 处理非法 JSON、缺字段、额外字段、超时和限流。
- 理解“格式合法”与“动作正确”的差别。

## 1. 模型调用的最小接口

不同提供方 API 不完全相同，但可以抽象为：

```text
ModelRequest
  - instructions: 系统目标与稳定约束
  - messages: 用户、助手、工具结果等上下文
  - tools: 当前身份可用的工具描述与输入 schema
  - response_format: 结构化输出约束（若支持）
  - sampling: temperature、最大输出等
  - metadata: trace_id、会话标识等非敏感关联信息

ModelResponse
  - final_text 或 tool_calls
  - finish_reason / refusal
  - usage / provider_request_id
  - raw_response（受控保存，注意隐私）
```

工具描述是模型选择动作的输入；真正的权限不应由模型或工具描述决定，而应由运行时根据当前用户身份和资源重新计算。

## 2. 一个明确的动作协议

为了让离线实验聚焦控制逻辑，本教程使用以下简化 JSON 协议：

```json
{"type":"tool_call","name":"calculator","arguments":{"expression":"2 + 3 * 4"}}
```

或：

```json
{"type":"final","answer":"14"}
```

规则：

1. 顶层必须是 JSON object，不能混入 Markdown 代码围栏或解释文字。
2. `type` 只能是 `tool_call` 或 `final`。
3. 工具调用必须有非空 `name` 和 object 类型的 `arguments`。
4. 最终回答必须有字符串 `answer`，且不应附带未声明字段。
5. 解析通过后，还要检查工具是否存在、参数是否符合该工具自己的 schema。

真实 SDK 可能使用独立 tool-call 字段，不要求模型手写 JSON。优先使用提供方原生结构化输出和工具调用能力，不要为统一抽象牺牲必要的错误信息。

## 3. 校验分四层

| 层 | 检查 | 失败后的动作 |
|---|---|---|
| 语法 | 是否为一个完整 JSON 值 | 返回可修正错误或终止，不盲目执行 |
| 协议 | 类型、必需字段、额外字段 | 拒绝动作并记录分类 |
| 工具 schema | 参数类型、范围、枚举、资源格式 | 不进入工具函数 |
| 业务授权 | 当前用户能否对目标资源执行该动作 | 拒绝或请求人工审批 |

不能用一条正则代替 JSON 解析，也不能因为 JSON 合法就跳过业务校验。

## 4. 失败不是同一种失败

```text
模型格式错误 -> 可选择一次带错误信息的修复请求
模型语义错误 -> 记录任务失败或进入验证分支
工具参数错误 -> 不执行，返回结构化参数错误
工具超时/限流 -> 按错误类型和幂等性决定重试
权限拒绝 -> 不应通过反复提示模型来绕过
```

对模型请求的重试与对业务工具的重试要分开。前者失败时可能尚未产生业务副作用；后者超时后，动作可能已经在服务端完成。

## 5. 密钥、隐私与原始响应

- 密钥仅由客户端持有，不出现在 messages、工具参数或日志中。
- 原始响应可能含个人信息、内部数据或模型生成的敏感内容，应设置保留周期和访问控制。
- trace 默认保存操作元数据、状态和用量；完整 prompt/response 采样记录需要额外策略。
- 不要把“模型拒绝回答”当作所有安全策略的实现，业务授权仍需确定性代码。

## 6. 最低实践：实现动作解析器

运行：

```bash
python code/ch02/structured_output.py
```

然后扩展 `parse_action`，至少覆盖：

- 合法工具调用和最终回答。
- 空输入、数组、代码围栏、缺少 `arguments`。
- 未知 `type`、空工具名、额外字段。
- 非 object 参数和空最终答案。

### 验收标准

每个错误都能被测试稳定触发；解析器不调用任何工具，也不偷偷修复危险动作。错误消息用于分类，不应把完整敏感输入无条件写入日志。

## 7. 真实模型实践

将同一组合法/非法输出样例放入模型适配器测试，并比较：

1. 只给文字格式说明。
2. 使用 JSON schema/结构化输出。
3. 使用提供方原生工具调用。

记录格式合规率、动作语义正确率、token 和延迟。不要把第 2 项的格式提升直接写成任务成功率提升。

## 8. 本章自测

1. JSON schema 校验通过，是否意味着模型选择了正确工具？
2. 为什么额外字段也应谨慎处理？
3. 工具超时后为什么不应一律自动重试？
4. 原生 tool calling 与手写 JSON 协议各适合什么学习和生产场景？

<details><summary>参考思路</summary>

1. 不意味着，schema 只约束结构；还需语义、环境和授权检查。
2. 额外字段可能表示模型误解协议，也可能在下游被错误消费；严格协议更容易定位问题。
3. 超时不知道服务端是否已提交副作用，需要幂等键、查询状态或人工核对。
4. 手写协议有助于学习控制流；生产优先用成熟原生能力，同时保留自己的校验和授权层。
</details>

## 9. 推荐资源

- [OpenAI Agents SDK: Tools](https://openai.github.io/openai-agents-python/tools/)：函数工具、schema、托管工具和工具执行管线。
- [OpenAI Agents SDK: Agents](https://openai.github.io/openai-agents-python/agents/)：指令、结构化输出、模型设置和运行时行为。
- [Google ADK: Technical Overview](https://google.github.io/adk-docs/get-started/about/)：Agent、Tool、Session、State 和 Artifact 的概念划分。

上一章：[Agent 全景](01-Agent全景.md)｜下一章：[最小 Agent Loop 与 ReAct](03-最小Agent-Loop与ReAct.md)
