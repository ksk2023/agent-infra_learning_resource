# 第 13 章：MLOps、评测、可观测性与成本

## 本章导学

一个系统能否长期运行，取决于是否知道“哪个版本产生了什么结果、现在是否健康、出问题能否回退、花了多少钱”。本章把这些贯穿训练与推理的能力串起来。

## 学习目标

- 建立代码、数据、配置、模型和环境的版本关联。
- 区分离线质量评测、性能 benchmark 与线上观测。
- 使用 metrics、logs、traces 和 SLO 诊断系统。
- 将安全、成本与发布回滚纳入工程闭环。

## 1. 可复现的最小血缘

一次实验或线上发布应能回答：

```text
哪份代码 + 哪份数据 + 哪份配置 + 哪个环境
  -> 哪个 checkpoint/模型制品
  -> 哪组离线评测
  -> 哪次部署
  -> 哪些线上指标
```

Git commit 只覆盖代码；数据快照、模型权重、容器 digest、依赖锁和随机性也需要记录。MLflow 可用于实验追踪和模型管理，DVC 可用于数据版本与流程协作，但它们不能替代你自己的血缘设计。

## 2. 三类评测不要混淆

| 类型 | 问题 | 示例 |
|---|---|---|
| 质量评测 | 输出是否正确、安全、满足任务？ | 准确率、任务集、人工评审 |
| 系统性能 | 在固定负载下有多快、多少资源？ | TTFT、TPOT、吞吐、显存 |
| 线上效果 | 真实流量中是否满足用户和业务目标？ | SLO、成功率、反馈、成本 |

通用 benchmark 分数不等于你的业务质量；单次性能测试也不等于线上 SLO。版本发布要有针对性的回归集。

## 3. Metrics、Logs、Traces 如何配合

- **Metrics**：低成本聚合趋势，如 QPS、错误率、P99、KV 使用率、GPU 温度。
- **Logs**：离散事件和错误细节，需结构化并控制敏感信息。
- **Traces**：跨网关、队列、引擎和存储的时间分布，定位延迟发生在哪段。

一个实用排查顺序：

```text
SLO 告警 -> 按版本/实例/租户缩小范围
  -> 看队列、错误和资源指标
  -> 用 trace 定位阶段
  -> 用日志和 profiler 深入具体实例
```

高基数标签会让时序系统成本和复杂度激增；不要把 request_id 无节制地放进 Prometheus label。

## 4. 训练和推理分别看什么

### 训练

- tokens/s、每步时间与数据等待。
- loss、梯度范数、NaN/Inf。
- 集合通信时间、worker 间偏斜。
- 显存、checkpoint 时长、失败和恢复。
- 有效训练进度，而不只是进程运行。

### 推理

- 到达率、在途/排队请求、准入与限流。
- TTFT、TPOT、ITL、E2E 的分位数。
- 输入/输出 tokens/s、goodput、错误与取消。
- KV 使用、cache 命中、batch 大小。
- 按模型版本和实例分组的资源与质量指标。

## 5. SLO 与错误预算

SLI 是实际测量指标，SLO 是目标。例如：

```text
在指定流量与请求分布下，95% 成功流式请求的 TTFT < 某阈值
```

一个完整 SLO 需说明测量窗口、请求范围、排除项和统计口径。错误预算是允许未达到目标的比例，用来平衡迭代与稳定性；不要把 SLO 写成脱离容量和成本的“永远 100%”。

## 6. 成本模型

简化成本：

```text
总成本 = 加速器 + CPU/内存 + 存储 + 网络 + 平台/运维 + 失败与空闲成本
单位成本 = 总成本 / 满足质量与 SLO 的有效工作量
```

每百万 token 成本必须注明输入/输出 token 口径、利用率、流量分布和是否含失败请求。低利用率时，单纯提高单实例峰值吞吐未必降低真实成本。

## 7. 供应链与运行时安全

- 模型权重、数据集和依赖都属于供应链输入，要记录来源与许可证。
- 谨慎对待 `trust_remote_code`、自定义反序列化和未审查的模型制品。
- 校验制品哈希/签名，限制网络与文件权限，隔离不可信执行。
- 日志与 trace 不记录明文密钥、隐私 prompt 或敏感输出。
- 多租户缓存、批处理和共享存储需要明确隔离边界。
- 安全扫描不能替代最小权限和人工审查。

## 8. 最低实践：设计一个可告警的面板

为第 10 章推理服务设计三层面板：

1. **用户面**：成功率、TTFT/TPOT/E2E 分位数、goodput。
2. **引擎面**：队列、batch、KV、cache、错误。
3. **资源面**：GPU/CPU/内存/网络/存储与实例状态。

为每条告警写“触发条件、影响、首个排查入口、缓解动作”，避免只有图表没有响应流程。

## 9. 开源资源

- [mlflow/mlflow](https://github.com/mlflow/mlflow)：实验、模型与 AI 工程管理。
- [treeverse/dvc](https://github.com/treeverse/dvc)：数据版本与 ML 实验协作；上游当前仓库入口以此为准。
- [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)：语言模型评测框架。
- [open-compass/opencompass](https://github.com/open-compass/opencompass)：多数据集 LLM 评测平台。
- [mlcommons/training](https://github.com/mlcommons/training) 与 [mlcommons/inference](https://github.com/mlcommons/inference)：MLPerf 训练/推理参考实现。
- [prometheus/prometheus](https://github.com/prometheus/prometheus)、[grafana/grafana](https://github.com/grafana/grafana)、[open-telemetry/opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python)：指标、展示与 tracing 生态。
- [NVIDIA/dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter)：向 Prometheus 生态导出 NVIDIA GPU 指标。

## 10. 本章自测

1. 为什么保存 Git commit 仍不足以复现训练？
2. 为什么 request_id 不适合直接作为 Prometheus label？
3. 通用 benchmark 分数提高能否直接证明线上业务改善？
4. 为什么单位成本要按满足质量和 SLO 的有效工作量计算？

<details><summary>参考思路</summary>

1. 数据、配置、依赖、模型状态与随机性同样影响结果。
2. 每个请求都产生新时间序列，导致高基数和存储/查询压力。
3. 不能，需要真实任务、流量、系统指标与线上效果验证。
4. 低质量或超过 SLO 的输出不是有效服务产能，忽略它会虚增成本优势。
</details>

上一章：[Serving 与云原生](12-Serving与云原生.md)｜下一章：[RL 后训练系统](14-RL后训练系统.md)
