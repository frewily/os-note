#!/usr/bin/env python3
"""批量给指定目录下的 .md 文件加 publish: true frontmatter。

用法:
    python3 scripts/mark_publish.py [目录] [--dry-run] [--exclude "路径或文件名后缀"]

默认排除（不标记发布）:
    - 个人规划 / 空笔记 / 复习追踪表
    - 所有名为 规则说明.md 的文件
    - 隐藏目录 (.git/.obsidian/.claude 等)

已带 publish 字段的文件会原地保留原值；publish: false 会改成 true。
"""
import argparse
import pathlib
import sys

# 默认排除：相对目标目录的路径后缀，命中即跳过
DEFAULT_EXCLUDES = {
    "规划/Java-AI工程方向成长路线规划.md",
    "JVM/JVM.md",
    "项目复盘/项目复盘.md",
    "八股/复习追踪表.md",
}
DEFAULT_EXCLUDE_NAMES = {"规则说明.md"}

SKIP_DIRS = {".git", ".obsidian", ".claude", ".claudian", ".trae", ".github", "node_modules", "__pycache__"}


def add_publish(text: str):
    """返回 (new_text, changed_flag)。不会破坏正文，只处理 frontmatter。"""
    if text.startswith("﻿"):  # strip BOM
        text = text[1:]
    lines = text.splitlines(keepends=True)

    if lines and lines[0].strip() == "---":
        # 已有 frontmatter：找到结束的 ---
        end = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end is None:
            return None, None  # frontmatter 未闭合，跳过不动
        body = lines[1:end]
        # 找已有 publish 字段
        pub = None
        for j, l in enumerate(body):
            if l.strip().startswith("publish"):
                pub = j
                break
        if pub is not None:
            key, _, rest = body[pub].partition(":")
            newline = f"{key.strip()}: true\n"
            if rest.strip() == "true":
                return text, False  # 已是 true
            body[pub] = newline
        else:
            body.insert(0, "publish: true\n")
        lines[1:end] = body
        return "".join(lines), True

    # 没有 frontmatter：在最顶部新建
    new = ["---\n", "publish: true\n", "---\n", "\n"]
    new.extend(lines)
    return "".join(new), True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", nargs="?", default=".", help="要扫描的目录，默认当前目录")
    ap.add_argument("--dry-run", action="store_true", help="只打印会改哪些文件，不写盘")
    ap.add_argument("--exclude", action="append", default=[], help="额外排除的路径后缀（可多次）")
    args = ap.parse_args()

    root = pathlib.Path(args.target)
    excludes = DEFAULT_EXCLUDES | set(args.exclude)

    changed, skipped_excl, skipped_done, skipped_bad = [], [], 0, []
    for p in sorted(root.rglob("*.md")):
        # 跳过隐藏目录
        rel = p.relative_to(root)
        if any(part.startswith(".") or part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        srel = rel.as_posix()
        # 默认排除
        if srel in excludes or rel.name in DEFAULT_EXCLUDE_NAMES:
            skipped_excl.append(srel)
            continue
        text = p.read_text(encoding="utf-8")
        if not text.strip():
            skipped_bad.append(srel)  # 空文件，不标记
            continue
        new, flag = add_publish(text)
        if new is None:
            skipped_bad.append(srel)
            continue
        if flag is False:
            skipped_done += 1  # 已 true，无需改
            continue
        changed.append(srel)
        if not args.dry_run:
            p.write_text(new, encoding="utf-8")

    print(f"目标目录: {root}")
    print(f"待标记   : {len(changed)}")
    if args.dry_run:
        for f in changed:
            print("  +", f)
    print(f"跳过(排除): {len(skipped_excl)}")
    print(f"跳过(已是true): {skipped_done}")
    print(f"跳过(空/异常): {len(skipped_bad)}")
    for f in skipped_bad:
        print("  ?", f)
    if args.dry_run and not changed:
        sys.exit(0)


if __name__ == "__main__":
    main()
