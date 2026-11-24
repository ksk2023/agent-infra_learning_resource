# CPU 最小实验

这些脚本只依赖 Python 标准库，用来验证公式、统计与调度逻辑。它们不是 GPU benchmark，也不模拟真实 kernel、显存带宽、网络拓扑或采样行为。

| 脚本 | 对应章节 | 用途 |
|---|---|---|
| `ch03/roofline.py` | 03 | Roofline、ridge point 与理论时间下界 |
| `ch05/memory_estimator.py` | 05、07 | 训练静态状态与显存预算 |
| `ch06/ring_allreduce.py` | 06、07 | Ring AllReduce 流量与理想模型 |
| `ch09/inference_metrics.py` | 09、13 | KV Cache、percentile 和 SLO 达标比例 |
| `ch10/batching_simulator.py` | 10、项目 P3 | Static/continuous batching 调度逻辑 |

在仓库根目录运行：

```bash
python code/ch03/roofline.py --flops 2e9 --bytes 100e6 --peak-flops 100e12 --bandwidth 1e12
python code/ch05/memory_estimator.py --params 7e9 --activation-gib 8 --workspace-gib 2
python code/ch06/ring_allreduce.py --size-mib 256 --ranks 8 --bandwidth-gbps 50 --latency-us 10
python code/ch09/inference_metrics.py kv --layers 32 --batch 8 --tokens 4096 --kv-heads 8 --head-dim 128 --dtype-bytes 2
python code/ch09/inference_metrics.py summarize
python code/ch10/batching_simulator.py
python -m unittest discover -s tests -v
```

扩展时优先增加测试和新的对照组，不要把教学模型包装成精确容量规划器。
