#!/usr/bin/env python3
"""同步 / 安装 playbook 的 skill 与模板。

三种模式：

1. playbook 模式（默认）：
   真源：仓库根 `skills/`（唯一可编辑处）。
   目标：本仓库 `.cursor/skills/`、`.claude/skills/`。

2. 安装模式（--install <项目路径>）：
   把本仓库的 skill **与其依赖的模板/参考文档**装到目标项目：
   - `skills/`     -> `<项目>/.cursor/skills/`、`<项目>/.claude/skills/`
   - `templates/`  -> `<项目>/templates/`（skill 正文里的 `templates/xxx.md` 引用据此解析）
   - `reference/`  -> `<项目>/reference/`（skill 正文里的 `reference/xxx.md` 引用据此解析；vendored-skills 除外）
   - `AGENTS.md`   -> `<项目>/AGENTS.md`（已存在则跳过，除非加 --force-agents）

3. 项目内同步模式（--project <项目路径>）：
   仅在目标项目内部把 `.claude/skills/` 同步到 `.cursor/skills/`。
   注意：这**不是**安装，不会从本仓库取 skill，也不分发模板。要装请用 --install。

用法：
    python scripts/sync-skills.py                            # playbook 模式：同步本仓库副本
    python scripts/sync-skills.py --check                    # playbook 模式：按内容校验
    python scripts/sync-skills.py --install <项目路径>        # 安装到项目（skill + 模板）
    python scripts/sync-skills.py --install <路径> --check    # 校验项目安装是否完整/漂移
    python scripts/sync-skills.py --project <项目路径>        # 项目内 .claude -> .cursor
    python scripts/sync-skills.py --project <路径> --check    # 项目内同步校验

注意：编辑 skill 请改真源（本仓库 `skills/`），再跑本脚本。
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_SKILLS = ROOT / "skills"
SRC_TEMPLATES = ROOT / "templates"
SRC_REFERENCE = ROOT / "reference"
SRC_AGENTS = ROOT / "AGENTS.md"

# 本仓库内的 skill 副本位置
PLAYBOOK_TARGETS = [ROOT / ".cursor" / "skills", ROOT / ".claude" / "skills"]

# 安装到目标项目时的 skill 目录（相对项目根）
INSTALL_SKILL_DIRS = [Path(".cursor") / "skills", Path(".claude") / "skills"]

# 匹配 skill 正文中对模板的引用，如 `templates/spec-template.md`
TEMPLATE_REF_RE = re.compile(r"templates/([\w.-]+\.md)")
# 匹配 skill 正文中对参考文档的引用，如 `reference/service-refactor-guide.md`
# 只捕获 reference/ 下直接的 .md 文件名；`reference/vendored-skills/...`（含 /）不匹配
REFERENCE_REF_RE = re.compile(r"reference/([\w.-]+\.md)")


# ---------- 通用工具 ----------


def iter_skill_dirs(src: Path):
    """返回 src 下所有包含 SKILL.md 的 skill 目录。"""
    if not src.exists():
        return
    for child in sorted(src.iterdir()):
        if child.is_dir() and (child / "SKILL.md").exists():
            yield child


def file_digest(path: Path) -> str:
    """单个文件的 SHA-256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dir_digest(skill_dir: Path) -> dict[str, str]:
    """skill 目录内所有文件的 {相对路径: SHA-256}，用于内容级比对。"""
    digests: dict[str, str] = {}
    for path in sorted(skill_dir.rglob("*")):
        if path.is_file():
            digests[path.relative_to(skill_dir).as_posix()] = file_digest(path)
    return digests


def copy_skill(src: Path, dst: Path) -> None:
    """整目录覆盖复制一个 skill。"""
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def referenced_templates(skill_dirs: list[Path]) -> set[str]:
    """扫描 skill 正文，收集被引用的模板文件名。"""
    names: set[str] = set()
    for skill in skill_dirs:
        for md in skill.rglob("*.md"):
            names.update(TEMPLATE_REF_RE.findall(md.read_text(encoding="utf-8")))
    return names


def referenced_references(skill_dirs: list[Path]) -> set[str]:
    """扫描 skill 正文，收集被引用的 reference/ 顶层文档名（不含 vendored-skills 子目录）。"""
    names: set[str] = set()
    for skill in skill_dirs:
        for md in skill.rglob("*.md"):
            names.update(REFERENCE_REF_RE.findall(md.read_text(encoding="utf-8")))
    return names


def compare_skills(src: Path, dst: Path, label: str) -> bool:
    """按内容比对两个 skill 根目录，返回是否存在差异（True = 有差异）。"""
    src_map = {d.name: d for d in iter_skill_dirs(src)}
    dst_map = {d.name: d for d in iter_skill_dirs(dst)}

    missing = sorted(set(src_map) - set(dst_map))
    extra = sorted(set(dst_map) - set(src_map))
    drifted = [
        name
        for name in sorted(set(src_map) & set(dst_map))
        if dir_digest(src_map[name]) != dir_digest(dst_map[name])
    ]

    if missing:
        print(f"[缺失] {label}：{missing}")
    if extra:
        print(f"[多余] {label}：{extra}")
    if drifted:
        print(f"[内容漂移] {label}：{drifted}")

    return bool(missing or extra or drifted)


def check_template_deps(skill_dirs: list[Path], templates_dir: Path, label: str) -> bool:
    """检查 skill 引用的模板在目标侧是否存在，返回是否有缺失。"""
    needed = referenced_templates(skill_dirs)
    if not needed:
        return False

    absent = sorted(name for name in needed if not (templates_dir / name).exists())
    if absent:
        print(f"[依赖缺失] {label} 缺少被引用的模板：{absent}")
    return bool(absent)


def check_reference_deps(skill_dirs: list[Path], reference_dir: Path, label: str) -> bool:
    """检查 skill 引用的 reference/ 顶层文档在目标侧是否存在，返回是否有缺失。"""
    needed = referenced_references(skill_dirs)
    if not needed:
        return False

    absent = sorted(name for name in needed if not (reference_dir / name).exists())
    if absent:
        print(f"[依赖缺失] {label} 缺少被引用的参考文档：{absent}")
    return bool(absent)


# session summary 模板必备字段（对齐 observe-session 的标准交接结构与自检）
SESSION_SUMMARY_TEMPLATE = "session-summary-template.md"
SESSION_SUMMARY_REQUIRED_FIELDS = [
    "session_id",
    "issue_id",
    "spec_id",
    "scope_changed",
    "facts",
    "decisions",
    "inferences",
    "external_blockers",
    "secrets_or_customer_content_read",
    "files_changed",
    "commit_or_pr",
    "next_owner",
    "next_action",
]


def check_session_summary_fields(templates_dir: Path, label: str) -> bool:
    """校验 session summary 模板含全部必备字段，返回是否有缺失。"""
    tpl = templates_dir / SESSION_SUMMARY_TEMPLATE
    if not tpl.exists():
        # 缺模板由 check_template_deps 报，这里不重复
        return False

    text = tpl.read_text(encoding="utf-8")
    missing = [f for f in SESSION_SUMMARY_REQUIRED_FIELDS if f not in text]
    if missing:
        print(f"[字段缺失] {label} {SESSION_SUMMARY_TEMPLATE} 缺少必备字段：{missing}")
    return bool(missing)


# ---------- playbook 模式 ----------


def sync_playbook() -> int:
    """从 skills/ 同步到本仓库 .cursor/ + .claude/。"""
    if not SRC_SKILLS.exists():
        print(f"[错误] 真源目录不存在：{SRC_SKILLS}")
        return 1

    skill_dirs = list(iter_skill_dirs(SRC_SKILLS))
    if not skill_dirs:
        print(f"[警告] {SRC_SKILLS} 下没有发现 skill")
        return 0

    for target in PLAYBOOK_TARGETS:
        target.mkdir(parents=True, exist_ok=True)
        for skill in skill_dirs:
            copy_skill(skill, target / skill.name)
        print(f"[完成] 已同步 {len(skill_dirs)} 个 skill -> {target.relative_to(ROOT)}")
    return 0


def check_playbook() -> int:
    """playbook 模式检查：内容级比对 + 模板依赖扫描。"""
    skill_dirs = list(iter_skill_dirs(SRC_SKILLS))
    need = False

    for target in PLAYBOOK_TARGETS:
        if compare_skills(SRC_SKILLS, target, str(target.relative_to(ROOT))):
            need = True

    if check_template_deps(skill_dirs, SRC_TEMPLATES, "templates/"):
        need = True

    if check_reference_deps(skill_dirs, SRC_REFERENCE, "reference/"):
        need = True

    if check_session_summary_fields(SRC_TEMPLATES, "templates/"):
        need = True

    if not need:
        print(f"[一致] {len(skill_dirs)} 个 skill 与模板/参考依赖均已就位")
    return 1 if need else 0


# ---------- 安装模式 ----------


def install_project(project: Path, force_agents: bool = False) -> int:
    """把本仓库 skill + 模板（+ AGENTS.md）安装到目标项目。"""
    skill_dirs = list(iter_skill_dirs(SRC_SKILLS))
    if not skill_dirs:
        print(f"[错误] 真源没有 skill：{SRC_SKILLS}")
        return 1

    project.mkdir(parents=True, exist_ok=True)

    # 1) skill
    for rel in INSTALL_SKILL_DIRS:
        target = project / rel
        target.mkdir(parents=True, exist_ok=True)
        for skill in skill_dirs:
            copy_skill(skill, target / skill.name)
        print(f"[完成] {len(skill_dirs)} 个 skill -> {rel.as_posix()}/")

    # 2) 模板（skill 正文按 `templates/xxx.md` 引用，必须一并分发）
    needed = referenced_templates(skill_dirs)
    dst_templates = project / "templates"
    dst_templates.mkdir(parents=True, exist_ok=True)
    copied, absent = 0, []
    for name in sorted(needed):
        src_file = SRC_TEMPLATES / name
        if src_file.exists():
            shutil.copy2(src_file, dst_templates / name)
            copied += 1
        else:
            absent.append(name)
    print(f"[完成] {copied} 个模板 -> templates/")
    if absent:
        print(f"[警告] 真源缺少被引用的模板（请修 playbook）：{absent}")

    # 3) 参考文档（skill 正文按 `reference/xxx.md` 引用，如指南；一并分发，vendored-skills 除外）
    ref_needed = referenced_references(skill_dirs)
    dst_reference = project / "reference"
    ref_copied, ref_absent = 0, []
    if ref_needed:
        dst_reference.mkdir(parents=True, exist_ok=True)
        for name in sorted(ref_needed):
            src_file = SRC_REFERENCE / name
            if src_file.exists():
                shutil.copy2(src_file, dst_reference / name)
                ref_copied += 1
            else:
                ref_absent.append(name)
        print(f"[完成] {ref_copied} 个参考文档 -> reference/")
        if ref_absent:
            print(f"[警告] 真源缺少被引用的参考文档（请修 playbook）：{ref_absent}")

    # 4) AGENTS.md（跨工具入口，默认不覆盖已有文件）
    dst_agents = project / "AGENTS.md"
    if not SRC_AGENTS.exists():
        print("[警告] 本仓库缺少 AGENTS.md，跳过")
    elif dst_agents.exists() and not force_agents:
        print("[跳过] 项目已有 AGENTS.md（如需覆盖加 --force-agents）")
    else:
        shutil.copy2(SRC_AGENTS, dst_agents)
        print("[完成] AGENTS.md -> 项目根")

    print(f"[安装完成] 目标项目：{project}")
    return 1 if (absent or ref_absent) else 0


def check_install(project: Path) -> int:
    """校验目标项目的安装是否完整（skill 内容 + 模板依赖）。"""
    skill_dirs = list(iter_skill_dirs(SRC_SKILLS))
    need = False

    for rel in INSTALL_SKILL_DIRS:
        if compare_skills(SRC_SKILLS, project / rel, rel.as_posix()):
            need = True

    if check_template_deps(skill_dirs, project / "templates", "项目 templates/"):
        need = True

    if check_reference_deps(skill_dirs, project / "reference", "项目 reference/"):
        need = True

    if check_session_summary_fields(project / "templates", "项目 templates/"):
        need = True

    if not (project / "AGENTS.md").exists():
        print("[提示] 项目缺少 AGENTS.md（跨工具入口）")

    if not need:
        print(f"[一致] 项目安装完整（{len(skill_dirs)} 个 skill + 模板/参考依赖）")
    return 1 if need else 0


# ---------- 项目内同步模式 ----------


def sync_project(project: Path) -> int:
    """项目内：.claude/skills/ -> .cursor/skills/（不涉及本仓库真源）。"""
    src = project / ".claude" / "skills"
    dst = project / ".cursor" / "skills"

    if not src.exists():
        print(f"[错误] 项目 .claude/skills/ 不存在：{src}")
        return 1

    skill_dirs = list(iter_skill_dirs(src))
    if not skill_dirs:
        print(f"[警告] {src} 下没有发现 skill")
        return 0

    dst.mkdir(parents=True, exist_ok=True)
    for skill in skill_dirs:
        copy_skill(skill, dst / skill.name)
    print(f"[完成] 已同步 {len(skill_dirs)} 个 skill -> .cursor/skills/（项目：{project}）")
    return 0


def check_project(project: Path) -> int:
    """项目内同步检查：内容级比对。"""
    src = project / ".claude" / "skills"
    if compare_skills(src, project / ".cursor" / "skills", ".cursor/skills/"):
        return 1

    count = len(list(iter_skill_dirs(src)))
    print(f"[一致] .claude/skills/ 与 .cursor/skills/ 已同步（{count} 个 skill）")
    return 0


# ---------- 入口 ----------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="同步 / 安装 playbook 的 skill 与模板",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--install", metavar="项目路径", help="从本仓库安装 skill + 模板到目标项目")
    group.add_argument("--project", metavar="项目路径", help="项目内 .claude/skills -> .cursor/skills（非安装）")
    parser.add_argument("--check", action="store_true", help="只检查不写入")
    parser.add_argument("--force-agents", action="store_true", help="安装时覆盖项目已有的 AGENTS.md")
    args = parser.parse_args()

    if args.install:
        project = Path(args.install).resolve()
        return check_install(project) if args.check else install_project(project, args.force_agents)

    if args.project:
        project = Path(args.project).resolve()
        return check_project(project) if args.check else sync_project(project)

    return check_playbook() if args.check else sync_playbook()


if __name__ == "__main__":
    sys.exit(main())
