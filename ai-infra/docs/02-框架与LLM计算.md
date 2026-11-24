# 第 02 章：深度学习框架与 LLM 计算

## 本章导学

要优化系统，先要知道模型代码最终变成了哪些张量、算子、内存分配和通信。本章不重复完整 Transformer 算法课，而是建立“模型定义到系统执行”的视角。

## 学习目标

- 解释张量、自动微分、计算图、算子与 runtime 的关系。
- 跟踪 decoder-only Transformer 的主要张量形状。
- 区分参数量、激活、梯度和优化器状态。
- 理解 eager 与编译执行的取舍。

## 1. 框架究竟做了什么

一个训练框架通常承担：

1. **表达**：用张量和算子描述模型。
2. **微分**：构建反向计算并产生梯度。
3. **执行**：将算子调度到 CPU/GPU 等后端。
4. **状态管理**：参数、buffer、优化器、随机数与分布式状态。
5. **扩展**：checkpoint、混合精度、分布式、编译与自定义算子。

在 eager 模式中，Python 执行与算子调用紧密相连，便于调试；图捕获与编译则给全局优化更多机会，但会引入 guard、重编译、图断点和更复杂的调试。

## 2. 从模型代码到设备

```text
Python 模型
  -> 张量与算子调用
  -> 自动微分图（训练时）
  -> 图捕获/编译（可选）
  -> 融合、布局与内存规划
  -> CUDA/Triton/厂商算子
  -> GPU 执行与显存访问
```

算子名称相同不代表执行相同。输入形状、dtype、布局、硬件和 backend 都可能选择不同 kernel。

## 3. Decoder-only Transformer 的计算骨架

设批次为 `B`、序列长度为 `T`、隐藏维度为 `D`：

```text
token ids: [B, T]
  -> embedding: [B, T, D]
  -> 重复 L 个 block：
       norm
       Q/K/V projection
       attention（训练通常看完整因果序列；decode 通常单步并读 KV）
       output projection
       residual
       norm + MLP + residual
  -> final norm
  -> LM head: [B, T, vocab]
```

训练与推理的差异不只是“有没有反向”：

- 训练常并行处理整段 token，并保存反向需要的激活。
- prefill 并行处理输入 token，建立 KV Cache。
- decode 每步处理一个新 token，却读取历史 KV 和模型权重。
- 在线 serving 还要处理不同长度请求的调度。

## 4. 三个有用的量级模型

### 4.1 参数存储

若参数个数为 `N`、每个参数 `w` 字节，则单份权重大小近似：

```text
weight_bytes ≈ N × w
```

真实制品还可能有 embedding、buffer、量化 scale、元数据和对齐开销。

### 4.2 训练 FLOPs

对 dense Transformer，常用粗略估算：

```text
training_FLOPs ≈ 6 × N × tokens
inference_weight_FLOPs ≈ 2 × N × generated_tokens
```

这里 `6` 来自矩阵乘法前向和反向的量级关系。它忽略或近似了 attention、激活重算、稀疏/MoE 激活参数差异等，只适合第一版预算，不是 profiler 的替代品。

### 4.3 全局 batch

```text
global_batch = micro_batch × grad_accum_steps × data_parallel_size
```

增加 gradient accumulation 不会增加同时驻留的 micro-batch 激活，但会增加每个优化器步骤的计算与通信间隔。

## 5. dtype 不是单纯的存储格式

FP32、BF16、FP16、FP8 和整数格式在以下方面不同：

- 数值范围与精度。
- Tensor Core 或其他硬件单元支持。
- 转换和缩放开销。
- 权重、激活、梯度、累加器分别使用什么 dtype。

“模型是 BF16”不代表所有归约、norm、优化器状态和通信也都是 BF16。阅读配置时要逐项确认。

## 6. 最低实践：做一份执行清单

任选 nanoGPT 或一个 Hugging Face 小模型，不运行也可以先静态阅读：

| 项目 | 要记录的内容 |
|---|---|
| 模型 | 层数、隐藏维度、head/KV head、词表、上下文长度 |
| 算子 | embedding、matmul、attention、norm、MLP、sampling |
| 状态 | 权重、梯度、优化器、激活、KV Cache |
| 精度 | 每类状态的 dtype |
| 执行 | eager/compile、设备、是否使用专用 attention backend |

然后回答：如果 `T` 翻倍，哪些项线性增长，哪些可能平方增长？在训练、prefill 和 decode 中答案是否相同？

## 7. GPU 实践：观察而不是猜测

在隔离环境中用 PyTorch profiler 观察一个小模型的几步执行：

- 比较 warmup 后 CPU 与 CUDA 时间。
- 找出耗时最高的算子与显存峰值。
- 改一个形状或 dtype，再观察 kernel 是否变化。
- 不把 profiler 的总耗时直接等同于墙上时间；异步执行需要正确同步。

## 8. 源码任务

- [karpathy/nanoGPT](https://github.com/karpathy/nanoGPT)：从小型 GPT 训练代码跟踪模型、训练循环和采样。
- [karpathy/llm.c](https://github.com/karpathy/llm.c)：对照 C/CUDA 实现，观察框架隐藏掉的显存与 kernel 细节。
- [pytorch/pytorch](https://github.com/pytorch/pytorch)：只围绕一个具体问题阅读，例如某算子 dispatch 或自动微分，不建议无目标通读。

## 9. 本章自测

1. 为什么同样的模型代码在不同输入形状下可能选择不同 kernel？
2. 为什么训练显存不能只按参数量计算？
3. `6NT` 能否直接用于所有 MoE 模型的精确成本核算？
4. eager 模式是否天然比编译模式慢？

<details><summary>参考思路</summary>

1. 形状影响后端选择、并行度、融合和是否达到硬件高效区间。
2. 还有梯度、优化器状态、激活、临时 buffer、碎片与通信 workspace。
3. 不能，它是有条件的近似；MoE 要区分总参数与每 token 激活参数。
4. 不是，取决于图捕获收益、kernel、重编译和工作负载；必须实测。
</details>

上一章：[AI Infra 全景](01-AI-Infra全景.md)｜下一章：[GPU 与 Roofline](03-GPU与Roofline.md)
