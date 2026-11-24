# 第 09 章：LLM 推理基础与性能指标

## 本章导学

LLM 推理不是一次普通前向计算，而是“输入并行处理 + 多步串行生成 + 动态请求调度”。本章建立 KV Cache、显存容量和延迟指标的定量基础。

## 学习目标

- 区分 prefill 与 decode 的计算和访存特征。
- 推导 KV Cache 大小，并理解 GQA/MQA 对容量的影响。
- 正确定义 TTFT、TPOT、ITL、E2E、吞吐与 goodput。
- 设计包含 warmup、并发和尾延迟的 benchmark。

## 1. Prefill 与 Decode

### Prefill

输入 prompt 的多个 token 可并行参与计算，生成每层 KV。较大矩阵计算更容易利用设备，但长输入也可能带来 attention 计算、显存和 TTFT 压力。

### Decode

每一步基于已有上下文生成一个 token：

1. 读取当前 token 表示和模型权重。
2. 计算新 Q/K/V。
3. 将新 K/V 写入 cache。
4. 读取历史 K/V 做 attention。
5. 采样/选择 token，进入下一步。

小 batch decode 常受权重和 KV 访存限制；但不能对所有模型、batch、硬件一概而论，仍应使用 roofline 和 profile 验证。

## 2. KV Cache 公式

对每个请求，设：

- `L`：层数；
- `T`：已缓存 token 数；
- `Hkv`：KV head 数；
- `Dh`：每个 head 的维度；
- `b`：每个元素的 dtype 字节数；
- `B`：并发序列数。

则近似：

```text
KV bytes = 2 × B × L × T × Hkv × Dh × b
```

最前面的 `2` 对应 K 和 V。对 MHA，`Hkv × Dh` 通常等于隐藏维度；GQA/MQA 中 `Hkv` 小于 query head 数，因此不能总用隐藏维度代替。

真实引擎还可能有 block 对齐、未填满页、元数据、临时 workspace、多卡复制或分片，所以公式用于估算逻辑 payload。

## 3. 推理显存预算

```text
总显存 ≈ 权重 + KV Cache + 激活/临时计算空间
       + 通信 workspace + runtime/碎片
```

长上下文、并发、输出长度和 batch 会共同消耗 KV。只看 prompt 长度会漏掉后续生成；只按权重能否加载判断服务能力，也会低估 OOM 风险。

## 4. 延迟与吞吐指标

| 指标 | 定义 | 注意 |
|---|---|---|
| TTFT | 请求到达到收到首个输出 token 的时间 | 需要流式时间戳；包含排队时要明确 |
| TPOT | 首个 token 后，生成后续 token 的平均间隔 | 常见算法需排除首 token，报告口径要一致 |
| ITL | 相邻输出 token 的间隔序列 | 可分析抖动与尾延迟 |
| E2E latency | 请求到达到完整响应结束 | 受输出长度影响 |
| Throughput | 单位时间完成请求或输出 token | 要区分 input/output tokens |
| Goodput | 满足指定质量/SLO 约束的有效吞吐 | SLO 必须先定义，不能只报均值 |

至少报告 P50/P95/P99、错误率、输入/输出长度分布和并发。将不同长度请求的 TPOT 直接平均可能掩盖 workload 差异。

## 5. Benchmark 的负载模型

- **Closed-loop**：固定数量客户端，完成后再发下一请求。客户端会随服务变慢而降低到达率。
- **Open-loop**：按预定到达过程发送，更适合研究排队和过载。
- **固定并发扫描**：便于画延迟—吞吐曲线，但需说明是否等价于真实流量。

应分别记录请求到达、开始执行、首 token、后续 token 和结束时间。若只测 HTTP 总时间，无法区分排队、prefill 和 decode。

## 6. 最低实践 A：KV Cache 估算

```bash
python code/ch09/inference_metrics.py kv \
  --layers 32 --batch 8 --tokens 4096 --kv-heads 8 \
  --head-dim 128 --dtype-bytes 2
```

然后：

1. 将 batch 和 token 数分别翻倍，观察线性关系。
2. 对比 MHA 与 GQA 的 `Hkv`。
3. 加上权重和 workspace，估算服务容量，不只报 KV 一项。

## 7. 最低实践 B：延迟分布

使用本仓库附带的示例数据：

```bash
python code/ch09/inference_metrics.py summarize
```

学习输出 P50/P95/P99 与 SLO 达标率。之后将自己的 benchmark 原始样本保存为 JSON，再复用该统计逻辑。

## 8. GPU 实践：真实引擎基线

在 vLLM 或 SGLang 中选择一个小模型：

- 固定模型、dtype、输入/输出长度和启动配置。
- warmup 后扫描多个并发或到达率。
- 采集 TTFT、TPOT、E2E、输出 tokens/s、错误率、显存。
- 将测量结果与 KV/roofline 估算对照。

完整推理课程可并行学习 [datawhalechina/zero-to-sglang](https://github.com/datawhalechina/zero-to-sglang)，其内容覆盖 KV Cache、benchmark、mini-sglang 与真实源码。

## 9. 本章自测

1. KV Cache 为什么避免重复计算，却增加显存压力？
2. 为什么低平均 TPOT 仍可能有很差的用户体验？
3. 为什么 closed-loop 测试可能低估过载时的排队？
4. GQA 对 KV Cache 公式的哪个参数产生直接影响？

<details><summary>参考思路</summary>

1. 缓存历史 K/V 供后续步复用，省去重复前向，但需保存随上下文和并发增长的状态。
2. 平均值隐藏 ITL 抖动、P99、长输出请求和失败。
3. 客户端等待完成后再发请求，服务变慢会反向降低负载到达率。
4. `Hkv`，KV head 数减少会降低逻辑 KV 容量。
</details>

上一章：[数据、Checkpoint 与容错](08-数据-Checkpoint与容错.md)｜下一章：[推理引擎核心](10-推理引擎核心.md)
