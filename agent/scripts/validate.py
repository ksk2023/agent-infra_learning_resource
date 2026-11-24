"""校验教程章节、必需文件与不离开教程根目录的相对 Markdown 链接。"""

from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DOCS = [
    "00-如何使用本教程.md",
    "01-Agent全景.md",
    "02-LLM接口与结构化输出.md",
    "03-最小Agent-Loop与ReAct.md",
    "04-工具设计与函数调用.md",
    "05-规划-反思与任务控制.md",
    "06-记忆与上下文工程.md",
    "07-RAG与证据驱动回答.md",
    "08-Agent-Runtime与持久化.md",
    "09-MCP-A2A与能力互操作.md",
    "10-多Agent协作与编排.md",
    "11-Agentic-RL与持续改进.md",
    "12-Agent评测与Benchmark.md",
    "13-可观测性-可靠性与成本.md",
    "14-安全-权限与人机协同.md",
    "15-综合项目与开源贡献.md",
]
REQUIRED_FILES = [
    "README.md", "ROADMAP.md", "code/README.md", "projects/README.md", "resources/README.md",
    "code/ch02/structured_output.py", "code/ch03/mini_agent.py", "code/ch05/dag_planner.py",
    "code/ch06/memory_context.py", "code/ch07/rag_lab.py", "code/ch08/checkpoint_runner.py",
    "code/ch12/eval_metrics.py", "code/ch13/trace_metrics.py", "code/ch14/policy_gate.py",
    "templates/learning-note.md", "templates/experiment-report.md", "templates/eval-task.md",
    "templates/source-reading.md", "templates/weekly-checkin.md", "tests/test_experiments.py",
]
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")


def validate() -> list[str]:
    errors: list[str] = []
    actual_docs = sorted(path.name for path in (ROOT / "docs").glob("*.md"))
    if actual_docs != EXPECTED_DOCS:
        missing = sorted(set(EXPECTED_DOCS) - set(actual_docs))
        extra = sorted(set(actual_docs) - set(EXPECTED_DOCS))
        errors.append(f"docs 章节必须恰好为 00–15；缺失={missing}，额外={extra}")

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"缺少必需文件：{relative}")

    checked_links = 0
    for source in sorted(ROOT.rglob("*.md")):
        text = source.read_text(encoding="utf-8")
        for match in LINK_PATTERN.finditer(text):
            raw_target = match.group(1).strip()
            if not raw_target or raw_target.startswith("#"):
                continue
            split = urlsplit(raw_target)
            if split.scheme.lower() in {"http", "https", "mailto"} or raw_target.startswith("//"):
                continue
            if split.scheme or split.netloc:
                errors.append(f"{source.relative_to(ROOT)}：不支持的链接协议 {raw_target}")
                continue
            local_target = unquote(split.path)
            if not local_target:
                continue
            checked_links += 1
            candidate = (source.parent / local_target).resolve()
            try:
                candidate.relative_to(ROOT)
            except ValueError:
                errors.append(f"{source.relative_to(ROOT)}：链接离开教程根目录 {raw_target}")
                continue
            if not candidate.exists():
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{source.relative_to(ROOT)}:{line}：链接目标不存在 {raw_target}")

    print(f"章节：{len(actual_docs)}；必需文件：{len(REQUIRED_FILES)}；本地链接：{checked_links}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"校验失败：{len(errors)} 个问题", file=sys.stderr)
        return 1
    print("教程结构与本地链接校验通过。外部 URL 未做在线可用性检查。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
