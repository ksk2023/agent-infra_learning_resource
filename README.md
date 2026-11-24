# AI Learning Resources

面向 AI 系统工程方向的系统化学习资料合集。不同方向放在独立子目录中，分别维护教程、实验、项目和参考资源。

## 内容导航

| 方向 | 目录 | 内容 |
|---|---|---|
| AI Infra | [ai-infra](ai-infra/README.md) | GPU、分布式训练、推理引擎、云原生、MLOps 与 RL Infra |
| Agent | [agent](agent/README.md) | Agent Loop、工具、RAG、Runtime、多 Agent、评测与安全 |

## AI Infra 快速开始

```bash
cd ai-infra
```

然后阅读：

- [教程首页](ai-infra/README.md)
- [16 周学习路线](ai-infra/ROADMAP.md)
- [GitHub 开源资源图谱](ai-infra/resources/README.md)
- [阶段项目](ai-infra/projects/README.md)

AI Infra 的 CPU 最小实验与文档检查也在其子目录中运行：

```bash
cd ai-infra
python -m unittest discover -s tests -v
python scripts/validate.py
```
