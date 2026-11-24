# 第 12 章：Serving、云原生与集群调度

## 本章导学

单进程 benchmark 证明引擎能跑，生产 serving 还要处理到达流量、版本、伸缩、故障、隔离和资源调度。本章将推理引擎放进一个可运营系统。

## 学习目标

- 设计网关、路由、引擎、缓存和监控组成的服务链路。
- 理解冷启动、模型加载、排队与 autoscaling 的关系。
- 解释 gang scheduling、拓扑感知和作业编排。
- 为灰度、回滚和多租户隔离制定方案。

## 1. 从引擎到服务

```text
DNS/负载均衡
  -> API 网关：鉴权、配额、限流、审计
  -> 路由器：模型/版本/租户/KV 感知
  -> 推理实例：队列、scheduler、模型 worker
  -> KV/前缀缓存与共享存储（可选）
  -> 指标、日志、trace、计费和告警
```

引擎负责高效执行，不代表网关、路由和平台可以省略。反过来，平台层也无法修复一个不适合 workload 的引擎配置。

## 2. 路由不只是 Round Robin

可考虑的路由信号：

- 模型与版本是否匹配。
- 实例健康、队列深度与可用 KV。
- 当前 batch、输入/输出长度估计。
- 前缀/KV 局部性。
- GPU 拓扑、预填充/解码资源池。
- 租户优先级与公平性。

KV-aware routing 可能提升缓存复用，但也可能把热点请求集中到少数实例。需要负载倾斜保护与一致性问题分析。

## 3. Autoscaling 为何容易失效

传统 CPU 指标可能不能代表 LLM 服务饱和度。更有用的信号包括：

- 请求队列与等待时间。
- 正在运行/等待的序列数。
- KV Cache 使用率。
- TTFT/TPOT 的 SLO 余量。
- tokens/s 与单位容量。

但扩容不是即时的：节点分配、镜像拉取、模型下载、权重加载、warmup 和缓存建立都可能耗时。突发流量下还要结合准入控制、队列上限、降级和容量预留。

## 4. Kubernetes 上的训练与推理

### 训练作业

- 多 worker 需要成组调度和启动，而不是各自随意占用资源。
- 需要 rank/服务发现、共享存储、故障重启和 checkpoint。
- GPU 互联与网络拓扑影响并行效率。

### 在线推理

- readiness 应反映模型可服务，而不只是进程启动。
- 滚动升级要处理长连接、流式请求和模型加载资源峰值。
- 节点 draining 需等待或安全迁移请求，不能只按无状态 HTTP 服务处理。

## 5. 相关开源组件的职责

| 组件 | 学习定位 |
|---|---|
| Kubernetes | 容器编排、资源与服务基础 |
| Kubeflow Trainer | Kubernetes 上的分布式训练/微调作业 |
| JobSet | 分布式 ML/HPC 作业抽象 |
| Volcano | 云原生批处理与调度 |
| KServe | Kubernetes 上的模型/生成式 AI 推理平台 |
| Ray | 分布式计算 runtime 与训练、 serving 等 AI 库 |
| NVIDIA Dynamo | 数据中心级分布式推理、路由与分离式 serving |
| Triton Inference Server | 多框架模型推理服务与后端生态 |

不要试图一次学完整个平台。先跑通一个工作负载，再读与问题相关的 CRD、controller 或 runtime 路径。

## 6. 灰度、回滚与隔离

模型服务发布至少要绑定：

- 模型制品与配置版本。
- 推理引擎与依赖版本。
- tokenizer/chat template。
- 质量评测结果与性能容量结果。
- 监控、告警和回滚条件。

多租户要考虑显存/队列隔离、配额、日志数据边界、缓存隔离、网络策略与模型加载安全。共享 prefix cache 时尤其要防止跨租户信息泄漏。

## 7. 最低实践：容量与故障设计

为一个假想服务写设计文档：

1. 定义输入/输出长度分布、到达率、TTFT/TPOT SLO。
2. 估算单实例容量，并给出需实测验证的假设。
3. 选择路由、队列、限流和 autoscaling 信号。
4. 设计模型冷启动和扩容期间的降级。
5. 画出实例故障、节点故障和发布回滚三条路径。

## 8. 实践路线

- 无集群：用本地 HTTP 服务模拟 readiness、队列、限流和指标，不伪造分布式结果。
- 单机容器：学习镜像、GPU 可见性、健康检查和优雅退出。
- Kubernetes 测试集群：部署一个小模型，演练滚动升级和节点维护。
- 多节点：再加入 KServe/Ray/Dynamo 等，围绕明确瓶颈选择组件。

## 9. 开源资源

- [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
- [kubeflow/trainer](https://github.com/kubeflow/trainer)
- [kubernetes-sigs/jobset](https://github.com/kubernetes-sigs/jobset)
- [volcano-sh/volcano](https://github.com/volcano-sh/volcano)
- [kserve/kserve](https://github.com/kserve/kserve)
- [ray-project/ray](https://github.com/ray-project/ray)
- [ai-dynamo/dynamo](https://github.com/ai-dynamo/dynamo)
- [triton-inference-server/server](https://github.com/triton-inference-server/server)

## 10. 本章自测

1. 为什么 readiness 不能只做 TCP 端口检查？
2. 为什么 KV-aware routing 可能造成热点？
3. 为什么发现 P99 超标后再扩容可能已经太晚？
4. 为什么滚动升级要额外考虑模型加载时的资源峰值？

<details><summary>参考思路</summary>

1. 端口开放不代表权重加载、warmup 和 worker 已可正常服务。
2. 相同前缀被导向同一实例可提高命中，也会集中负载。
3. 扩容包含节点、镜像、模型和 warmup 的冷启动时间。
4. 新旧实例可能同时占用内存/显存/存储与网络，导致资源不足或流量抖动。
</details>

上一章：[模型压缩与多端推理](11-模型压缩与多端推理.md)｜下一章：[MLOps、评测与可观测性](13-MLOps-评测与可观测性.md)
