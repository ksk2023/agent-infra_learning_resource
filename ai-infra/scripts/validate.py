"""校验教程结构、本地 Markdown 链接，并可选择检查 GitHub 仓库可达性。"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
REPO_PATTERN = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/?$")


def local_validation() -> tuple[list[str], set[str]]:
    errors: list[str] = []
    repos: set[str] = set()
    markdown_files = sorted(ROOT.rglob("*.md"))
    docs = sorted((ROOT / "docs").glob("*.md"))

    if len(docs) != 16:
        errors.append(f"docs 应有 16 章，实际为 {len(docs)}")

    for number in range(16):
        if not list((ROOT / "docs").glob(f"{number:02d}-*.md")):
            errors.append(f"缺少第 {number:02d} 章")

    for markdown in markdown_files:
        text = markdown.read_text(encoding="utf-8")
        for target in LINK_PATTERN.findall(text):
            target = target.strip()
            repo_match = REPO_PATTERN.fullmatch(target)
            if repo_match:
                repos.add("https://github.com/" + "/".join(repo_match.groups()))
            if target.startswith(("https://", "http://", "mailto:")):
                continue
            path_text = target.split("#", 1)[0]
            if not path_text:
                continue
            destination = (markdown.parent / path_text).resolve()
            try:
                destination.relative_to(ROOT)
            except ValueError:
                errors.append(f"{markdown.relative_to(ROOT)}: 链接越出工作区 {target}")
                continue
            if not destination.exists():
                errors.append(f"{markdown.relative_to(ROOT)}: 本地链接不存在 {target}")

    return errors, repos


def check_remote(url: str) -> tuple[str, str]:
    request = Request(url, method="HEAD", headers={"User-Agent": "AI-Infra-Guide-Link-Check"})
    try:
        with urlopen(request, timeout=15) as response:
            return url, f"HTTP {response.status}"
    except HTTPError as error:
        if error.code in (403, 429):
            return url, f"限流/权限，未判定失效：HTTP {error.code}"
        return url, f"HTTP {error.code}"
    except (URLError, TimeoutError) as error:
        return url, f"网络未验证：{error}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote", action="store_true", help="额外 HEAD 检查 GitHub 仓库链接")
    args = parser.parse_args()

    errors, repos = local_validation()
    print(f"Markdown 文件：{len(list(ROOT.rglob('*.md')))}")
    print(f"GitHub 仓库链接：{len(repos)}")
    if errors:
        print("本地校验失败：")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("本地结构与链接校验通过。")

    if args.remote:
        failures = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            for url, status in executor.map(check_remote, sorted(repos)):
                if not status.startswith("HTTP 2") and not status.startswith("HTTP 3"):
                    failures.append((url, status))
        if failures:
            print("远程链接需复核：")
            for url, status in failures:
                print(f"- {url}: {status}")
            sys.exit(2)
        print(f"远程仓库可达性检查通过：{len(repos)} 个。")


if __name__ == "__main__":
    main()
