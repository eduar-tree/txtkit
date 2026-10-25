#!/usr/bin/env python3
"""txtkit —— 纯标准库处理大文本文件的三个小工具。

    count    按行/词/字符统计，支持中文字符
    find     按正则查找并显示上下文行
    slice    按行区间或字符区间截取

用法:
    python txtkit.py count file.txt
    python txtkit.py find file.txt "TODO|FIXME" --context 2
    python txtkit.py slice file.txt --lines 10:30
    python txtkit.py slice file.txt --chars 0:500
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    """按 UTF-8 读取，失败时退回 latin-1（宁可显示乱码也不要崩）。"""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def count_text(text: str) -> dict[str, int]:
    lines = text.splitlines()
    words = re.findall(r"[A-Za-z0-9_']+", text)
    cjk = re.findall(r"[\u4e00-\u9fff]", text)
    other_words = len(re.findall(r"[\u4e00-\u9fff]", text))
    return {
        "characters": len(text),
        "characters_no_space": len(re.sub(r"\s", "", text)),
        "lines": len(lines),
        "blank_lines": sum(1 for line in lines if not line.strip()),
        "words_latin": len(words),
        "cjk_characters": other_words,
        "total_words": len(words) + other_words,
    }


def cmd_count(args) -> int:
    text = read_text(Path(args.file))
    stats = count_text(text)
    if args.json:
        import json
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0
    width = max(len(k) for k in stats)
    for key, value in stats.items():
        print(f"{key.ljust(width)}  {value}")
    return 0


def cmd_find(args) -> int:
    text = read_text(Path(args.file))
    pattern = re.compile(args.pattern)
    lines = text.splitlines()
    hits = 0
    for index, line in enumerate(lines):
        if not pattern.search(line):
            continue
        hits += 1
        start = max(0, index - args.context)
        end = min(len(lines), index + args.context + 1)
        for j in range(start, end):
            marker = ">" if j == index else " "
            print(f"{marker} {j + 1:>5} | {lines[j]}")
        if args.context and end < len(lines):
            print("  ...  ")
    print(f"\n匹配 {hits} 处。")
    return 0 if hits else 1


def cmd_slice(args) -> int:
    text = read_text(Path(args.file))
    if args.lines:
        start, end = _parse_range(args.lines)
        lines = text.splitlines()
        start = max(1, start)
        end = min(len(lines), end)
        for index in range(start - 1, end):
            print(f"{index + 1:>5} | {lines[index]}")
        return 0
    if args.chars:
        start, end = _parse_range(args.chars)
        print(text[start:end])
        return 0
    print("txtkit slice: 需要 --lines 或 --chars", file=sys.stderr)
    return 2


def _parse_range(spec: str) -> tuple[int, int]:
    """解析 "10:30" / "10" / "10:" / ":30"。"""
    text = spec.strip()
    if ":" in text:
        left, _, right = text.partition(":")
        start = int(left) if left.strip() else 0
        end = int(right) if right.strip() else 10 ** 9
    else:
        start = int(text)
        end = start + 1
    return start, end


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="txtkit",
        description="纯标准库的大文本处理工具：count / find / slice",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("count", help="统计字符/行/词")
    c.add_argument("file")
    c.add_argument("--json", action="store_true")
    c.set_defaults(fn=cmd_count)

    f = sub.add_parser("find", help="正则查找并显示上下文")
    f.add_argument("file")
    f.add_argument("pattern")
    f.add_argument("--context", type=int, default=0, help="上下各显示几行")
    f.set_defaults(fn=cmd_find)

    s = sub.add_parser("slice", help="截取行区间或字符区间")
    s.add_argument("file")
    s.add_argument("--lines", help="行区间，如 10:30")
    s.add_argument("--chars", help="字符区间，如 0:500")
    s.set_defaults(fn=cmd_slice)

    args = parser.parse_args(argv)
    path = Path(args.file)
    if not path.exists():
        print(f"txtkit: 找不到文件 {path}", file=sys.stderr)
        return 2
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
