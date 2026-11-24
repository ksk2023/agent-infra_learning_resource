# 第 03 章：GPU 体系结构与 Roofline

## 本章导学

性能优化的第一步不是换参数，而是判断瓶颈属于计算、内存、通信还是开销。本章用 Roofline 建立可计算的直觉。

## 学习目标

- 理解 GPU 的并行执行与存储层次。
- 计算算术强度、ridge point 和理论性能上界。
- 区分 compute-bound、memory-bound 与 overhead-bound。
- 能解释 decode 为什么常常受显存带宽限制。

## 1. GPU 的四个观察尺度

1. **执行**：大量线程以 SIMT 方式执行，warp 内分支分歧会影响效率。
2. **存储**：寄存器、shared memory、缓存、HBM 的容量、带宽与延迟不同。
3. **并行组织**：grid、block、thread 如何映射到数据。
4. **主机协作**：CPU 启动 kernel、拷贝数据、同步和调度也会产生开销。

“GPU 有很多核心”不是充分条件。没有足够并行度、数据复用或合并访存，核心可能大量等待。

## 2. Roofline 模型

定义：

```text
算术强度 I = FLOPs / 访问内存字节数
可获得性能 P = min(峰值计算性能 P_peak, 内存带宽 B × I)
ridge point = P_peak / B
```

等价的时间下界（忽略启动、通信等）：

```text
T >= max(FLOPs / P_peak, bytes / B)
```

当 `I < P_peak/B` 时倾向 memory-bound；当 `I` 更高时倾向 compute-bound。这里的内存层次必须一致：用 HBM 字节数就配 HBM 带宽，不能混入 on-chip 带宽。

### 一个纯演示例子

假设某假想设备峰值为 `100 TFLOP/s`、带宽为 `1 TB/s`，某算子执行 `2 GFLOP` 并访问 `100 MB`：

```text
I = 2e9 / 100e6 = 20 FLOP/byte
ridge = 100e12 / 1e12 = 100 FLOP/byte
P <= min(100 TFLOP/s, 20 TFLOP/s) = 20 TFLOP/s
```

它更可能受内存限制。以上数字只是演示，不对应具体 GPU。

## 3. 三类瓶颈与信号

| 类型 | 常见信号 | 优先尝试 |
|---|---|---|
| 计算受限 | 接近有效计算峰值，矩阵规模充分 | 更高效算法、低精度、减少计算 |
| 内存受限 | 大量搬运、算术强度低 | 融合、复用、tiling、减少读写 |
| 开销受限 | 小 kernel 很多、CPU 启动频繁、同步多 | 合并、CUDA Graph、异步流水、减少 Python 开销 |

实际还有通信受限、排队受限和数据供给受限。Roofline 给出的是上界，不是实测值。

## 4. 为什么 decode 常受带宽约束

自回归 decode 每生成一个 token，都要使用模型参数进行一轮计算。小 batch 时，矩阵乘的有效计算量相对权重读取量不足，权重和 KV 的搬运往往成为主要成本。

简化理解：

```text
每步时间 >= 权重与 KV 读取字节数 / 有效带宽
```

增大 batch 可以摊薄权重读取，提高算术强度；但也增加 KV 容量、单步计算和排队，因此吞吐与延迟必须一起看。长上下文 prefill、大 batch GEMM 和高并发 decode 的瓶颈可能不同。

## 5. 性能分析的正确顺序

```text
定义工作负载
  -> 验证输出正确
  -> 测墙上时间与资源
  -> 计算理论上界
  -> profiler 定位时间分布
  -> 修改一个变量
  -> 复测并检查质量回归
```

如果实测远低于理论值，不一定马上写新 kernel：可能有同步、冷启动、数据加载、kernel launch、通信或 profiler 失真。

## 6. 最低实践：运行 Roofline 计算器

```bash
python code/ch03/roofline.py --flops 2e9 --bytes 100e6 \
  --peak-flops 100e12 --bandwidth 1e12
```

再完成三组分析：

1. 固定 FLOPs，将访存字节降低一半，性能上界如何变化？
2. 固定访存，将 FLOPs 增加四倍，瓶颈何时改变？
3. 找一个你自己的算子，写出 FLOPs 和字节数的推导，不只填计算器。

## 7. GPU 实践

- 用 Nsight Systems 或 PyTorch profiler 先看时间线，再用 Nsight Compute 深入单个 kernel。
- 比较同一操作的多个 shape：小 shape 可能 overhead-bound，大 shape 才进入 roofline 讨论。
- 测量时做 warmup 和正确同步，保留原始 trace。

## 8. 开源资源

- [jax-ml/scaling-book](https://github.com/jax-ml/scaling-book)：从 roofline、网络与并行策略理解训练和推理扩展；以 TPU 为主，但方法可迁移到 GPU。
- [gpu-mode/lectures](https://github.com/gpu-mode/lectures)：CUDA、Triton、CUTLASS、profiling 与 kernel 主题。
- [NVIDIA/cuda-samples](https://github.com/NVIDIA/cuda-samples)：CUDA 官方示例。
- [microsoft/AI-System](https://github.com/microsoft/AI-System)：矩阵运算与体系结构章节。

## 9. 本章自测

1. 峰值 FLOPS 翻倍但带宽不变，所有算子都会加速吗？
2. 算术强度是否只由硬件决定？
3. 为什么 GPU 利用率高仍可能远离 roofline 上界？
4. decode 增大 batch 的代价是什么？

<details><summary>参考思路</summary>

1. 不会，memory-bound 和 overhead-bound 算子可能几乎不受益。
2. 不是，还由算法、shape、数据复用和实现决定。
3. 利用率是活动比例，不直接表示有效 FLOP 效率、访存效率或有用工作比例。
4. 更多 KV 显存、更大计算量和排队，尾延迟可能上升。
</details>

上一章：[框架与 LLM 计算](02-框架与LLM计算.md)｜下一章：[CUDA、Triton 与 AI 编译](04-CUDA-Triton与AI编译.md)
