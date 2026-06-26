#!/usr/bin/env python3
"""同步 skill 到各工具目录。

两种模式：

1. playbook 模式（默认）：
   真源：仓库根 `skills/`（唯一可编辑处）。
   目标：`.cursor/skills/`（Cursor）、`.claude/skills/`（Claude Code）。

2. 项目模式（--project <路径>）：
   在指定项目内同步 `.cursor/skills/` ↔ `.claude/skills/`。
   以 .claude/skills/ 为源（Claude Code 常为原始工具），同步到 .cursor/skills/。

用法：
    python scripts/sync-skills.py                          # playbook 模式：同步 playbook skill
    python scripts/sync-skills.py --check                  # playbook 模式：检查是否需同步
    python scripts/sync-skills.py --project <项目路径>      # 项目模式：同步项目内 skill
    python scripts/sync-skills.py --project <路径> --check  # 项目模式：检查

注意：编辑 skill 请改真源（playbook 的 skills/ 或项目的 .claude/skills/），再跑本脚本。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "skills"
TARGETS = [ROOT / ".cursor" / "skills", ROOT / ".claude" / "skills"]


def iter_skill_dirs(src: Path):
    """返回 src 下所有包含 SKILL.md 的 skill 目录。"""
    for child in sorted(src.iterdir()):
        if child.is_dir() and (child / "SKILL.md").exists():
            yield child


def sync_playbook() -> int:
    """playbook 模式：从 skills/ 同步到 .cursor/ + .claude/"""
    if not SRC.exists():
        print(f"[错误] 真源目录不存在：{SRC}")
        return 1

    skill_dirs = list(iter_skill_dirs(SRC))
    if not skill_dirs:
        print(f"[警告] {SRC} 下没有发现 skill")
        return 0

    for target in TARGETS:
        target.mkdir(parents=True, exist_ok=True)
        for skill in skill_dirs:
            dest = target / skill.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(skill, dest)
        print(f"[完成] 已同步 {len(skill_dirs)} 个 skill -> {target.relative_to(ROOT)}")
    return 0


def sync_project(project_path: Path) -> int:
    """项目模式：从 .claude/skills/ 同步到 .cursor/skills/"""
    src = project_path / ".claude" / "skills"
    dst = project_path / ".cursor" / "skills"

    if not src.exists():
        print(f"[错误] 项目 .claude/skills/ 不存在：{src}")
        return 1

    skill_dirs = list(iter_skill_dirs(src))
    if not skill_dirs:
        print(f"[警告] {src} 下没有发现 skill")
        return 0

    dst.mkdir(parents=True, exist_ok=True)
    for skill in skill_dirs:
        dest = dst / skill.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(skill, dest)
    print(f"[完成] 已同步 {len(skill_dirs)} 个 skill -> .cursor/skills/ （项目：{project_path}）")
    return 0


def check_playbook() -> int:
    """playbook 模式检查"""
    src_names = {d.name for d in iter_skill_dirs(SRC)} if SRC.exists() else set()
    need = False
    for target in TARGETS:
        dst_names = (
            {d.name for d in target.iterdir() if (d / "SKILL.md").exists()}
            if target.exists()
            else set()
        )
        if dst_names != src_names:
            need = True
            print(f"[需同步] {target.relative_to(ROOT)}：{sorted(src_names - dst_names)}")
    return 1 if need else 0


def check_project(project_path: Path) -> int:
    """项目模式检查"""
    src = project_path / ".claude" / "skills"
    dst = project_path / ".cursor" / "skills"

    src_names = (
        {d.name for d in src.iterdir() if (d / "SKILL.md").exists()}
        if src.exists()
        else set()
    )
    dst_names = (
        {d.name for d in dst.iterdir() if (d / "SKILL.md").exists()}
        if dst.exists()
        else set()
    )

    if src_names != dst_names:
        missing = src_names - dst_names
        extra = dst_names - src_names
        if missing:
            print(f"[需同步] .cursor/skills/ 缺少：{sorted(missing)}")
        if extra:
            print(f"[需同步] .cursor/skills/ 多出：{sorted(extra)}")
        return 1

    print(f"[一致] .claude/skills/ 与 .cursor/skills/ 已同步（{len(src_names)} 个 skill）")
    return 0


if __name__ == "__main__":
    is_check = "--check" in sys.argv

    # 解析 --project 参数
    project_path = None
    if "--project" in sys.argv:
        idx = sys.argv.index("--project")
        if idx + 1 < len(sys.argv):
            project_path = Path(sys.argv[idx + 1]).resolve()
        else:
            print("[错误] --project 需要一个路径参数")
            sys.exit(1)

    if project_path:
        # 项目模式
        if is_check:
            sys.exit(check_project(project_path))
        else:
            sys.exit(sync_project(project_path))
    else:
        # playbook 模式
        if is_check:
            sys.exit(check_playbook())
        else:
            sys.exit(sync_playbook())
