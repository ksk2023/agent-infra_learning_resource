# 第 09 章：MCP、A2A 与能力互操作

## 本章导学

当工具、能力和 Agent 来自不同进程或团队时，需要协议而不是临时字符串约定。本章建立 MCP、A2A 与 Skills 的边界，并强调互操作不等于自动可信。

## 学习目标

- 解释 MCP host、client、server 与 tools/resources/prompts。
- 理解 A2A 的发现、任务与产物交换所解决的问题。
- 区分 Tool、Skill、MCP 和 A2A。
- 将版本协商、身份、授权、审批和审计纳入协议接入。

## 1. MCP：连接 Agent 与工具/数据

MCP 采用 host—client—server 架构。Host 是协调连接的 AI 应用；client 维护到某个 server 的连接；server 提供上下文与能力。数据层定义协议对象和能力，传输层处理本地或远程通信。

典型流程：

```text
Host 配置 Server
  -> Client 建立连接并协商版本/能力
  -> 发现 tools、resources、prompts
  -> Host 将经过筛选的工具描述提供给模型
  -> 模型请求 tool call
  -> Host/Client 做参数、身份、权限与审批检查
  -> Server 执行并返回结构化结果
  -> Host 将结果作为受控观察写回上下文
```

MCP 不规定 Agent 应如何规划或管理全部上下文，也不替代应用的权限系统。具体原语、传输和已弃用功能会随协议版本演进，应以当前官方 specification 为准。

## 2. Tools、Resources 与 Prompts

| 原语 | 含义 | 例子 |
|---|---|---|
| Tools | 可执行动作 | 查询数据库、创建工单 |
| Resources | 可读取的数据/上下文 | 文档、schema、文件内容 |
| Prompts | 可复用交互模板 | 带示例的任务模板 |

资源内容也可能是不可信文本；工具描述也会影响模型选择。安装 server 时的审查不能代替运行时检查，工具列表变化应触发重新审查或至少版本与差异记录。

## 3. A2A：连接独立 Agent

A2A 面向不同 Agent 应用之间的互操作。一个调用方可发现远程 Agent 的能力，提交任务，接收状态更新与 artifact，而无需共享其内部提示词、工具或记忆。

概念性映射：

```text
Agent Card / 能力发现
Task / 长运行任务及状态
Message / 交互信息
Artifact / 可交付结果
Streaming / Push / 轮询等更新机制（以版本规范为准）
```

MCP 与 A2A 可以互补：一个 Agent 通过 MCP 使用工具，再通过 A2A 将子任务交给另一个独立 Agent。不要把 A2A 当作同一进程内函数调用的必要替代品。

## 4. Tool、Skill、MCP、A2A 的区别

| 概念 | 核心回答 | 是否天然提供执行权限 |
|---|---|---|
| Tool | “调用什么接口？” | 否，仍需身份与授权 |
| Skill | “完成一类任务遵循什么流程、脚本和验收？” | 否，技能内容也需审查 |
| MCP | “Host 如何标准化接入工具和数据？” | 否，协议不代替安全控制 |
| A2A | “独立 Agent 如何发现、委派和交换任务结果？” | 否，跨 Agent 信任需另行建立 |

Skill 通常是版本化的流程知识与资源包；它可能指导模型使用工具，但不是工具本身。把所有概念都包装成“插件”会模糊安全和维护边界。

## 5. 互操作的安全边界

- **来源与供应链**：确认 server/SDK/Skill 来源、许可证、签名或哈希与依赖。
- **版本**：记录协商结果；不要把不同版本字段和示例混用。
- **最小暴露**：只加载当前任务需要的 server 和工具，避免工具描述污染整个上下文。
- **授权**：按用户和租户重新校验资源，不信任模型传入的身份或 server 自描述。
- **审批**：高风险工具及跨 Agent 高影响委派需要具体、可撤销的批准。
- **内容**：tool description、resource、artifact 和远程 Agent 输出均按不可信输入处理。
- **审计**：保存操作元数据、版本、调用关联和状态，不默认记录敏感全文。

## 6. 最低实践：做一张协议与信任边界图

选择一个“本地研究 Agent 调用远程旅行 Agent，并读取文档”的场景：

1. 标出 Host、MCP Client、文档 Server、本地 Agent、远程 Agent 和用户。
2. 将读文档、搜索、创建行程、付款分别归类为 resource/tool/A2A task 或本地确定性动作。
3. 为每条连接写出身份、版本、数据范围、超时、审计与撤销方式。
4. 为一个 Skill 写出触发条件、所需工具、步骤、验收和回归测试。
5. 说明远程 Agent 返回的 artifact 为什么不能自动获得本地执行权限。

### 验收标准

不是只画 Logo；每条协议连接都有明确数据/控制语义和信任边界。

## 7. 源码任务

用官方 SDK 建一个只读、假数据的 MCP server，通过 Inspector 或客户端检查工具列表与 schema。随后修改工具描述，观察客户端是否检测变化。不要把实验 server 连接到真实密钥或生产数据。

## 8. 本章自测

1. 接入 MCP 后，工具参数是否可以跳过应用层授权？
2. A2A 与 MCP 是否能互相完全替代？
3. Skill 与 Tool 的主要差异是什么？
4. 为什么远程 Agent 的输出仍需作为不可信输入处理？

<details><summary>参考思路</summary>

1. 不可以，协议负责交互格式，业务授权仍由可信应用/服务端执行。
2. 不能，主要边界分别是 Agent—工具/数据与 Agent—Agent，可组合使用。
3. Skill 主要是流程知识与资源包，Tool 是可调用接口；两者都需版本和安全管理。
4. 输出可能错误、被注入或超出授权范围，不能因来自“另一个 Agent”就默认可信。
</details>

## 9. 推荐资源

- [MCP 官方架构](https://modelcontextprotocol.io/docs/learn/architecture) 与 [Specification](https://modelcontextprotocol.io/specification/latest)：以当前规范核对协议版本、原语和传输。
- [A2A 官方文档](https://a2a-protocol.org/latest/) 与 [a2aproject/A2A](https://github.com/a2aproject/A2A)：Agent 互操作、规范、SDK 和示例。
- [OpenAI Agents SDK: MCP](https://openai.github.io/openai-agents-python/mcp/)：一种成熟 Agent SDK 的 MCP 接入方式。

上一章：[Agent Runtime 与持久化](08-Agent-Runtime与持久化.md)｜下一章：[多 Agent 协作与编排](10-多Agent协作与编排.md)
