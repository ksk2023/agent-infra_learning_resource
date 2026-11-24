# 第 04 章：CUDA、Triton 与 AI 编译

## 本章导学

Kernel 优化不是背几个技巧，而是在正确性约束下，改变并行映射、数据复用、访存和执行开销。本章建立从 CUDA 到 Triton、再到图编译的共同语言。

## 学习目标

- 写出并验证一个简单 GPU kernel 的映射逻辑。
- 解释合并访存、tiling、shared memory、reduction 和 occupancy。
- 理解 Triton 与 CUDA 的抽象层级差异。
- 了解 PyTorch 编译栈与通用 AI 编译器的作用。

## 1. CUDA Kernel 的最小思维模型

写一个 kernel 前先回答：

1. 每个线程负责哪些输出元素？
2. 边界条件如何处理？
3. 输入会被哪些线程重复读取？
4. 哪些数据应放进更快的存储？
5. 哪些线程需要同步？
6. 如何证明结果与参考实现一致？

以向量加法为例，映射很简单；以矩阵乘法为例，核心就变成 tile 如何复用 A/B 数据、如何累加和如何避免越界。

## 2. 常见优化手段及其边界

| 手段 | 解决什么 | 可能的代价 |
|---|---|---|
| 合并访存 | 减少低效全局内存事务 | 需要调整布局或索引 |
| Tiling | 提高数据复用、降低 HBM 访问 | shared memory/寄存器压力 |
| 算子融合 | 减少中间张量读写和 launch | 寄存器增加、调试更复杂 |
| 并行归约 | 提高 sum/max/softmax 等效率 | 同步和数值顺序问题 |
| 提高 occupancy | 隐藏延迟 | 并非越高越好，可能牺牲每线程资源 |
| CUDA Graph | 降低重复 launch/CPU 开销 | 捕获条件与动态 shape 限制 |

不要把这些当成固定清单。优化前先用 profile 证明对应瓶颈存在。

## 3. 正确性优先于速度

一个算子的验证至少包括：

- 多种 shape，包括空、极小、非整除和大输入。
- 不同 dtype 与边界值。
- 与高精度参考实现比较合理容差。
- 非默认 stride/layout（若接口允许）。
- 确定性要求与浮点归约顺序说明。
- 性能测试与正确性测试分开，但使用同一实现。

`torch.allclose` 的容差不是 universal truth；低精度、累加顺序和数学性质需要分别分析。

## 4. Triton 的定位

Triton 用较高层的 Python 风格语言表达 tiled GPU 计算，适合学习：

- program 与数据块的映射。
- mask 和边界处理。
- block pointer/索引与内存访问。
- reduction、matmul、softmax、attention 等模式。
- autotune 配置与性能对照。

它不是“自动保证最快”。编译器版本、硬件、shape、配置搜索和 backend 都会影响结果。

## 5. 从图到 kernel：AI 编译做什么

典型优化包括：

- 计算图化简与常量折叠。
- 算子融合和布局转换。
- 内存规划与 buffer 复用。
- shape 特化与自动调优。
- 针对硬件生成或选择 kernel。

PyTorch 中可将 TorchDynamo 的图捕获、AOTAutograd 的训练图处理和 TorchInductor 的代码生成分开理解。出现图断点或频繁重编译时，不能只盯生成 kernel，还要检查 Python 控制流与动态 shape。

通用编译方向可继续看 MLIR、XLA、TVM；推理引擎则可能对手写 kernel、模板库和编译路线做组合。

## 6. 最低实践：两条路线选一

### 路线 A：GPU Puzzles

完成 [srush/GPU-Puzzles](https://github.com/srush/GPU-Puzzles) 的 map、zip、reduction、prefix sum 和 matmul 相关题目。每题记录：

- 线程到数据的映射。
- 全局/共享内存访问次数。
- 同步位置。
- 最初错误及修复。

### 路线 B：Triton 小算子

在有支持 GPU 的隔离环境中实现 elementwise 或 reduction：

1. 先写参考实现。
2. 写 Triton kernel 并通过多组 shape 测试。
3. warmup 后测中位数与分布。
4. 改变 block 配置，解释何时收益消失。

## 7. 源码任务

- [triton-lang/triton](https://github.com/triton-lang/triton)：先读教程与测试，再进入编译器实现。
- [Dao-AILab/flash-attention](https://github.com/Dao-AILab/flash-attention)：理解 IO-aware attention，而不是只记“融合 attention”。
- [flashinfer-ai/flashinfer](https://github.com/flashinfer-ai/flashinfer)：观察 serving 场景中的 attention/kernel 组织。
- [NVIDIA/cuda-samples](https://github.com/NVIDIA/cuda-samples)：按具体 CUDA 特性查示例。

## 8. 本章自测

1. 为什么 occupancy 更高不必然更快？
2. 为什么融合通常能降低内存开销？
3. 为什么 benchmark 前必须先验证数值正确性？
4. Triton 是否消除了理解 GPU 存储层次的必要？

<details><summary>参考思路</summary>

1. 更多常驻 warp 可能降低寄存器/shared memory 可用量，且性能可能已由其他瓶颈决定。
2. 中间结果可留在寄存器或片上存储，减少写回再读取及 launch。
3. 错误结果也可能“很快”，低精度还需定义合理容差。
4. 没有，tile、访存、并行和资源限制仍决定性能。
</details>

上一章：[GPU 与 Roofline](03-GPU与Roofline.md)｜下一章：[单机训练优化](05-单机训练优化.md)
