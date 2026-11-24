# GitHub 开源资源图谱

本图谱按“学什么、何时学、用来做什么”组织，而不是按 Star 排名。GitHub 项目会持续新增、迁移和归档，因此这是一份覆盖 AI Infra 主要方向的精选主干与扩展索引，不声称静态穷尽所有仓库。

使用建议：每章只选 1 个主干资源 + 1 个真实项目深入；标为“索引”的仓库用于查资料，无需从头读完。所有项目的代码、文档、模型和数据许可证分别以上游为准。

## 1. 系统课程、教材与学习路线

| 资源 | 适合学习 | 使用建议 |
|---|---|---|
| [microsoft/AI-System](https://github.com/microsoft/AI-System) | 中文 AI 系统、框架、体系结构、分布式、推理、编译 | 通用主干 |
| [chenzomi12/AISystem](https://github.com/chenzomi12/AISystem) | 中文硬件、编译、推理与框架课件 | 配合在线文档，按需下载 |
| [harvard-edge/cs249r_book](https://github.com/harvard-edge/cs249r_book) | 机器学习系统、TinyTorch、集群、边缘与配套实验 | 查看各卷成熟状态和分组件许可证 |
| [stanford-cs336/spring2025-lectures](https://github.com/stanford-cs336/spring2025-lectures) | 从零构建 LLM、训练、kernel、并行与推理 | 模型与系统交叉主干 |
| [llmsystem/llmsystem.github.io](https://github.com/llmsystem/llmsystem.github.io) | CMU LLM Systems 历年课程入口 | 高阶课程导航 |
| [gpu-mode/lectures](https://github.com/gpu-mode/lectures) | CUDA、Triton、CUTLASS、profiling、kernel | GPU 方向主干 |
| [srush/GPU-Puzzles](https://github.com/srush/GPU-Puzzles) | 交互式 GPU/CUDA 编程 | 配合第 04 章逐题实现 |
| [srush/Tensor-Puzzles](https://github.com/srush/Tensor-Puzzles) | PyTorch/张量操作与广播直觉 | 前置练习 |
| [jax-ml/scaling-book](https://github.com/jax-ml/scaling-book) | Roofline、TPU/GPU、并行与推理定量分析 | 训练/推理进阶主干 |
| [datawhalechina/happy-llm](https://github.com/datawhalechina/happy-llm) | LLM 原理与从零构建 | 模型前置补给 |
| [datawhalechina/zero-to-sglang](https://github.com/datawhalechina/zero-to-sglang) | 从零构建 mini 推理引擎、读 SGLang、做 PR | 推理方向核心课程 |
| [TheKernelZ/AI-Infra-Roadmap](https://github.com/TheKernelZ/AI-Infra-Roadmap) | 推理加速路线、项目和模板 | 推理岗位补充路线 |
| [HuaizhengZhang/AI-Infra-from-Zero-to-Hero](https://github.com/HuaizhengZhang/AI-Infra-from-Zero-to-Hero) | AI 系统论文、训练、推理与行业资料 | 研究索引 |
| [pacoxu/AI-Infra](https://github.com/pacoxu/AI-Infra) | 云原生训练、推理和平台资料 | 平台方向索引 |
| [1duo/awesome-ai-infrastructures](https://github.com/1duo/awesome-ai-infrastructures) | 训练/推理生产基础设施分类 | 横向查组件 |
| [PKUFlyingPig/cs-self-learning](https://github.com/PKUFlyingPig/cs-self-learning) | 体系结构、操作系统、分布式等 CS 基础 | 按需补前置 |

## 2. 框架、模型训练与微调

| 资源 | 主要学习点 | 对应章节 |
|---|---|---|
| [pytorch/pytorch](https://github.com/pytorch/pytorch) | 张量、autograd、profiler、DDP、FSDP、编译 | 02、05–08 |
| [jax-ml/jax](https://github.com/jax-ml/jax) | 可组合变换、JAX 与加速器计算 | 02、04、07 |
| [tensorflow/tensorflow](https://github.com/tensorflow/tensorflow) | 图执行、训练和部署生态 | 02、04 |
| [huggingface/transformers](https://github.com/huggingface/transformers) | 模型定义、权重与生成接口 | 02、09 |
| [huggingface/accelerate](https://github.com/huggingface/accelerate) | 设备、混合精度与分布式训练抽象 | 05–07 |
| [huggingface/peft](https://github.com/huggingface/peft) | LoRA 等参数高效微调 | 05、07 |
| [huggingface/trl](https://github.com/huggingface/trl) | SFT、偏好与 RL 后训练接口 | 14 |
| [karpathy/nanoGPT](https://github.com/karpathy/nanoGPT) | 精简 GPT 训练与采样 | 02、05 |
| [karpathy/llm.c](https://github.com/karpathy/llm.c) | C/CUDA 的大模型训练实现 | 02、04、05 |
| [pytorch/torchtitan](https://github.com/pytorch/torchtitan) | PyTorch 原生大模型训练平台与可组合并行 | 07、08 |
| [NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM) | 大规模 Transformer、TP/PP/EP 与训练优化 | 07、08 |
| [deepspeedai/DeepSpeed](https://github.com/deepspeedai/DeepSpeed) | ZeRO、分布式训练与优化 | 05–07 |
| [hpcaitech/ColossalAI](https://github.com/hpcaitech/ColossalAI) | 多维并行与大模型训练 | 07 |
| [huggingface/picotron](https://github.com/huggingface/picotron) | 面向教学的精简多维并行 | 07 优先读 |
| [huggingface/nanotron](https://github.com/huggingface/nanotron) | 大模型并行训练实现 | 07 对照 Picotron |
| [EleutherAI/gpt-neox](https://github.com/EleutherAI/gpt-neox) | 开源 GPT 训练代码与分布式实践 | 07 |
| [NVIDIA-NeMo/NeMo](https://github.com/NVIDIA-NeMo/NeMo) | 大模型训练、定制与部署工具链 | 07、08 |
| [hiyouga/LlamaFactory](https://github.com/hiyouga/LlamaFactory) | 统一高效微调与多模型支持 | 05、07 |
| [modelscope/ms-swift](https://github.com/modelscope/ms-swift) | 多模型、多模态微调与后训练 | 05、07、14 |
| [axolotl-ai-cloud/axolotl](https://github.com/axolotl-ai-cloud/axolotl) | 配置驱动的开源模型微调 | 05、07 |
| [unslothai/unsloth](https://github.com/unslothai/unsloth) | 面向资源效率的微调与 kernel 优化实践 | 05、11 |

## 3. GPU、集合通信、Kernel 与编译

| 资源 | 主要学习点 | 建议 |
|---|---|---|
| [NVIDIA/cuda-samples](https://github.com/NVIDIA/cuda-samples) | CUDA 官方特性示例 | 按主题查，不必全跑 |
| [NVIDIA/nccl](https://github.com/NVIDIA/nccl) | GPU 集合通信 | 结合 DDP/FSDP 阅读 |
| [NVIDIA/nccl-tests](https://github.com/NVIDIA/nccl-tests) | AllReduce 等通信 benchmark | 多卡性能基线 |
| [open-mpi/ompi](https://github.com/open-mpi/ompi) | MPI 与高性能计算通信 | 分布式基础选修 |
| [triton-lang/triton](https://github.com/triton-lang/triton) | Triton 语言与编译器 | 先教程和测试，后源码 |
| [Dao-AILab/flash-attention](https://github.com/Dao-AILab/flash-attention) | IO-aware 精确 attention | Kernel 进阶主干 |
| [flashinfer-ai/flashinfer](https://github.com/flashinfer-ai/flashinfer) | 面向 LLM serving 的 kernel 库 | 推理 kernel 进阶 |
| [NVIDIA/cutlass](https://github.com/NVIDIA/cutlass) | CUDA C++ 高性能矩阵与模板抽象 | 有 CUDA 基础后学习 |
| [NVIDIA/TransformerEngine](https://github.com/NVIDIA/TransformerEngine) | Transformer 加速与低精度训练 | 训练 kernel 进阶 |
| [pytorch/ao](https://github.com/pytorch/ao) | 低精度、量化、稀疏与训练/推理优化 | 第 11 章主干 |
| [llvm/llvm-project](https://github.com/llvm/llvm-project) | LLVM/MLIR 编译基础设施 | 编译原理进阶 |
| [apache/tvm](https://github.com/apache/tvm) | 深度学习编译与自动调优 | AI 编译选修 |
| [openxla/xla](https://github.com/openxla/xla) | XLA 编译与加速生态 | JAX/编译选修 |
| [tinygrad/tinygrad](https://github.com/tinygrad/tinygrad) | 精简框架、设备和代码生成 | 小型实现对照 |
| [ROCm/ROCm](https://github.com/ROCm/ROCm) | AMD GPU 软件栈 | 非 NVIDIA 路线入口 |

## 4. 推理引擎、运行时与 KV 系统

| 资源 | 主要学习点 | 使用建议 |
|---|---|---|
| [vllm-project/vllm](https://github.com/vllm-project/vllm) | 高吞吐 LLM 推理、serving、调度与 KV | 推理主干 |
| [sgl-project/sglang](https://github.com/sgl-project/sglang) | 高性能 LLM/多模态 serving、RadixAttention | 配合 zero-to-sglang |
| [sgl-project/mini-sglang](https://github.com/sgl-project/mini-sglang) | 精简推理引擎实现 | 读真实引擎前学习 |
| [NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) | NVIDIA GPU 上的 LLM 优化与运行时 | 硬件相关进阶 |
| [NVIDIA/TensorRT](https://github.com/NVIDIA/TensorRT) | 通用 GPU 推理优化与图/runtime | 传统与生成式推理 |
| [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | 本地/端侧 C/C++ LLM 推理 | CPU/端侧主干 |
| [ggml-org/ggml](https://github.com/ggml-org/ggml) | 底层张量库与设备后端 | 对照框架实现 |
| [ONNX Runtime 官方文档](https://onnxruntime.ai/) | 跨平台 ONNX 推理与执行提供者 | 本次核验时 GitHub 主仓库无法访问，暂以官方文档为入口 |
| [triton-inference-server/server](https://github.com/triton-inference-server/server) | 多框架模型服务、backend 与动态批处理 | 通用 serving |
| [InternLM/lmdeploy](https://github.com/InternLM/lmdeploy) | LLM 压缩、部署和 serving | 中文生态对照 |
| [mlc-ai/mlc-llm](https://github.com/mlc-ai/mlc-llm) | 编译与多设备 LLM 部署 | 编译/端侧选修 |
| [deepspeedai/DeepSpeed-MII](https://github.com/deepspeedai/DeepSpeed-MII) | DeepSpeed 推理服务接口 | DeepSpeed 路线选修 |
| [LMCache/LMCache](https://github.com/LMCache/LMCache) | KV Cache 层、复用与分层 | 长上下文/缓存进阶 |
| [ai-dynamo/dynamo](https://github.com/ai-dynamo/dynamo) | 分布式推理、路由与分离式 serving | 集群推理进阶 |
| [bentoml/BentoML](https://github.com/bentoml/BentoML) | 模型服务封装与部署 | 服务工程选修 |
| [tensorflow/serving](https://github.com/tensorflow/serving) | 通用模型 serving 架构 | 传统模型服务对照 |

## 5. 云原生、调度与分布式平台

| 资源 | 主要学习点 | 使用建议 |
|---|---|---|
| [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes) | 容器编排、资源、服务与控制器 | 平台基础 |
| [kubernetes-sigs/jobset](https://github.com/kubernetes-sigs/jobset) | 分布式 ML/HPC 作业 API | 训练平台主干 |
| [kubeflow/trainer](https://github.com/kubeflow/trainer) | Kubernetes 分布式训练与微调 | 训练平台主干 |
| [kubeflow/kubeflow](https://github.com/kubeflow/kubeflow) | Kubernetes 上 ML 工具平台 | 按需了解全局 |
| [volcano-sh/volcano](https://github.com/volcano-sh/volcano) | 云原生批处理与调度 | gang/batch 调度 |
| [ray-project/ray](https://github.com/ray-project/ray) | 分布式 runtime、Train/Serve/RLlib 等 | 分布式 AI 主干 |
| [kserve/kserve](https://github.com/kserve/kserve) | Kubernetes 模型与生成式推理平台 | 推理平台主干 |
| [NVIDIA/k8s-device-plugin](https://github.com/NVIDIA/k8s-device-plugin) | Kubernetes NVIDIA GPU 设备暴露 | GPU 集群基础 |
| [SchedMD/slurm](https://github.com/SchedMD/slurm) | HPC  workload 与资源调度 | 训练集群选修 |

## 6. 数据、实验、模型与流程管理

| 资源 | 主要学习点 | 使用建议 |
|---|---|---|
| [huggingface/datasets](https://github.com/huggingface/datasets) | 数据集访问与处理 | 训练数据基础 |
| [mlflow/mlflow](https://github.com/mlflow/mlflow) | 实验追踪、模型与 AI 工程管理 | MLOps 主干 |
| [treeverse/dvc](https://github.com/treeverse/dvc) | 数据版本、流程与实验协作 | 可复现性主干 |
| [feast-dev/feast](https://github.com/feast-dev/feast) | Feature store 与特征服务 | 传统 ML 平台选修 |
| [apache/airflow](https://github.com/apache/airflow) | 工作流编排 | 数据/训练流程选修 |
| [argoproj/argo-workflows](https://github.com/argoproj/argo-workflows) | Kubernetes 原生工作流 | 云原生流程选修 |
| [great-expectations/great_expectations](https://github.com/great-expectations/great_expectations) | 数据质量验证 | 数据治理选修 |
| [apache/spark](https://github.com/apache/spark) | 大规模数据处理 | 数据前置处理 |
| [delta-io/delta](https://github.com/delta-io/delta) | Lakehouse 表与数据管理 | 数据平台选修 |
| [apache/iceberg](https://github.com/apache/iceberg) | 大规模分析表格式 | 数据平台选修 |
| [minio/minio](https://github.com/minio/minio) | 对象存储 | checkpoint/数据实验 |
| [facebookresearch/faiss](https://github.com/facebookresearch/faiss) | 向量相似度搜索 | 检索基础设施选修 |
| [milvus-io/milvus](https://github.com/milvus-io/milvus) | 向量数据库与检索服务 | RAG 基础设施选修 |

## 7. 评测、Benchmark 与可观测性

| 资源 | 主要学习点 | 使用建议 |
|---|---|---|
| [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) | 语言模型 few-shot 等评测 | 质量基线 |
| [open-compass/opencompass](https://github.com/open-compass/opencompass) | 多任务、多模型 LLM 评测 | 中文/多任务对照 |
| [stanford-crfm/helm](https://github.com/stanford-crfm/helm) |  holistic 语言模型评测 | 研究方法选修 |
| [mlcommons/training](https://github.com/mlcommons/training) | MLPerf 训练参考实现 | 训练 benchmark |
| [mlcommons/inference](https://github.com/mlcommons/inference) | MLPerf 推理参考实现 | 推理 benchmark |
| [prometheus/prometheus](https://github.com/prometheus/prometheus) | 指标采集、时序与告警 | 可观测性主干 |
| [grafana/grafana](https://github.com/grafana/grafana) | 指标与观测数据可视化 | 面板实践 |
| [open-telemetry/opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python) | Python traces/metrics/logs API 与 SDK | 服务链路追踪 |
| [NVIDIA/dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter) | NVIDIA GPU telemetry 到 Prometheus | GPU 集群观测 |

## 8. RL 后训练与 Agentic RL Infra

| 资源 | 主要学习点 | 使用建议 |
|---|---|---|
| [huggingface/trl](https://github.com/huggingface/trl) | Transformer 后训练与 RL 接口 | 入门主线 |
| [verl-project/verl](https://github.com/verl-project/verl) | HybridFlow、灵活高效 RL 后训练 | RL Infra 主干 |
| [OpenRLHF/OpenRLHF](https://github.com/OpenRLHF/OpenRLHF) | Ray、训练与推理引擎组合的 RL 框架 | 分布式 RL 对照 |
| [THUDM/slime](https://github.com/THUDM/slime) | RL scaling 与训练—推理协同 | 进阶主线 |
| [NVIDIA-NeMo/RL](https://github.com/NVIDIA-NeMo/RL) | 可扩展模型强化学习 | NeMo 路线选修 |
| [NVIDIA-NeMo/Gym](https://github.com/NVIDIA-NeMo/Gym) | 模型/Agent 环境与验证器生态 | Agentic RL 选修 |
| [ray-project/ray](https://github.com/ray-project/ray) | Actor、task、对象和资源调度 | RL 分布式前置 |

## 9. 如何维护这份图谱

发现新项目或迁移时，按以下标准筛选：

1. 是否解决一个清晰的 AI Infra 问题。
2. 是否有文档、测试、示例或许可证。
3. 是否仍维护，或虽停止维护但具有明确经典学习价值。
4. 是否与已有资源互补，而不是重复堆链接。
5. 是否能在课程中对应一个概念、实验或源码任务。

不要把未体验的 benchmark、营销文案或自动生成声明直接写入结论。性能数据只在保留硬件、版本、配置、workload 和原始结果时才有学习价值。
