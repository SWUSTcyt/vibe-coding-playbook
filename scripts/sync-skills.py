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
   - `docs/`       -> `<项目>/docs/`（只分发 SHARED_DOCS 白名单里、且被 skill 引用的指南，如 e2e-verify-guide.md；
                      `docs/issues-log.md` 等项目自有文件不分发，避免覆盖）
   - `AGENTS.md`   -> `<项目>/AGENTS.md`（已存在则跳过，除非加 --force-agents）

   `--install <路径> --check` 对 skill、模板、参考文档、共享指南都按内容哈希比对：
   文件缺失或与本仓库版本不一致都报错（安装本来就会覆盖这些文件，不一致即安装过旧）。

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
SRC_DOCS = ROOT / "docs"
SRC_AGENTS = ROOT / "AGENTS.md"

# docs/ 下由 playbook 维护、需要随安装分发的指南（白名单）。
# skill 也引用 `docs/issues-log.md` 等项目自有文件，那些不能分发，否则会覆盖项目记录。
SHARED_DOCS = {"e2e-verify-guide.md"}

# 本仓库内的 skill 副本位置
PLAYBOOK_TARGETS = [ROOT / ".cursor" / "skills", ROOT / ".claude" / "skills"]

# 安装到目标项目时的 skill 目录（相对项目根）
INSTALL_SKILL_DIRS = [Path(".cursor") / "skills", Path(".claude") / "skills"]

# 匹配 skill 正文中对模板的引用，如 `templates/spec-template.md`
TEMPLATE_REF_RE = re.compile(r"templates/([\w.-]+\.md)")
# 匹配 skill 正文中对参考文档的引用，如 `reference/service-refactor-guide.md`
# 只捕获 reference/ 下直接的 .md 文件名；`reference/vendored-skills/...`（含 /）不匹配
REFERENCE_REF_RE = re.compile(r"reference/([\w.-]+\.md)")
# 匹配 skill 正文中对 docs/ 顶层文档的引用，如 `docs/e2e-verify-guide.md`；只有命中 SHARED_DOCS 的才分发
DOCS_REF_RE = re.compile(r"docs/([\w.-]+\.md)")


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


def referenced_shared_docs(skill_dirs: list[Path]) -> set[str]:
    """扫描 skill 正文，收集被引用、且在 SHARED_DOCS 白名单里的 docs/ 指南。"""
    names: set[str] = set()
    for skill in skill_dirs:
        for md in skill.rglob("*.md"):
            names.update(DOCS_REF_RE.findall(md.read_text(encoding="utf-8")))
    return names & SHARED_DOCS


def check_dep_files(names: set[str], src_dir: Path, dst_dir: Path, label: str, kind: str) -> bool:
    """检查依赖文件在目标侧是否存在且与真源内容一致，返回是否有问题。

    src_dir 与 dst_dir 相同（playbook 自检）时只查存在。
    """
    absent: list[str] = []
    stale: list[str] = []
    same_dir = src_dir.resolve() == dst_dir.resolve()
    for name in sorted(names):
        dst_file = dst_dir / name
        if not dst_file.exists():
            absent.append(name)
            continue
        src_file = src_dir / name
        if not same_dir and src_file.exists() and file_digest(src_file) != file_digest(dst_file):
            stale.append(name)

    if absent:
        print(f"[依赖缺失] {label} 缺少被引用的{kind}：{absent}")
    if stale:
        print(f"[内容过旧] {label} 的{kind}与本仓库版本不一致（请重新 --install）：{stale}")
    return bool(absent or stale)


def copy_dep_files(names: set[str], src_dir: Path, dst_dir: Path) -> tuple[int, list[str]]:
    """把依赖文件从真源复制到目标目录，返回（复制数，真源缺失列表）。"""
    copied, absent = 0, []
    if not names:
        return copied, absent
    dst_dir.mkdir(parents=True, exist_ok=True)
    for name in sorted(names):
        src_file = src_dir / name
        if src_file.exists():
            shutil.copy2(src_file, dst_dir / name)
            copied += 1
        else:
            absent.append(name)
    return copied, absent


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
    """检查 skill 引用的模板在目标侧是否存在且内容与真源一致。"""
    return check_dep_files(referenced_templates(skill_dirs), SRC_TEMPLATES, templates_dir, label, "模板")


def check_reference_deps(skill_dirs: list[Path], reference_dir: Path, label: str) -> bool:
    """检查 skill 引用的 reference/ 顶层文档在目标侧是否存在且内容与真源一致。"""
    return check_dep_files(referenced_references(skill_dirs), SRC_REFERENCE, reference_dir, label, "参考文档")


def check_docs_deps(skill_dirs: list[Path], docs_dir: Path, label: str) -> bool:
    """检查 skill 引用的共享指南（SHARED_DOCS）在目标侧是否存在且内容与真源一致。"""
    return check_dep_files(referenced_shared_docs(skill_dirs), SRC_DOCS, docs_dir, label, "共享指南")


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

    if check_docs_deps(skill_dirs, SRC_DOCS, "docs/"):
        need = True

    if check_session_summary_fields(SRC_TEMPLATES, "templates/"):
        need = True

    if not need:
        print(f"[一致] {len(skill_dirs)} 个 skill 与模板/参考/共享指南依赖均已就位")
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
    (project / "templates").mkdir(parents=True, exist_ok=True)
    copied, absent = copy_dep_files(referenced_templates(skill_dirs), SRC_TEMPLATES, project / "templates")
    print(f"[完成] {copied} 个模板 -> templates/")
    if absent:
        print(f"[警告] 真源缺少被引用的模板（请修 playbook）：{absent}")

    # 3) 参考文档（skill 正文按 `reference/xxx.md` 引用，如指南；一并分发，vendored-skills 除外）
    ref_copied, ref_absent = copy_dep_files(
        referenced_references(skill_dirs), SRC_REFERENCE, project / "reference"
    )
    if ref_copied or ref_absent:
        print(f"[完成] {ref_copied} 个参考文档 -> reference/")
    if ref_absent:
        print(f"[警告] 真源缺少被引用的参考文档（请修 playbook）：{ref_absent}")

    # 4) 共享指南（只分发 SHARED_DOCS 白名单里、被 skill 引用的 docs/ 文档）
    docs_copied, docs_absent = copy_dep_files(
        referenced_shared_docs(skill_dirs), SRC_DOCS, project / "docs"
    )
    if docs_copied or docs_absent:
        print(f"[完成] {docs_copied} 个共享指南 -> docs/")
    if docs_absent:
        print(f"[警告] 真源缺少被引用的共享指南（请修 playbook）：{docs_absent}")

    # 5) AGENTS.md（跨工具入口，默认不覆盖已有文件）
    dst_agents = project / "AGENTS.md"
    if not SRC_AGENTS.exists():
        print("[警告] 本仓库缺少 AGENTS.md，跳过")
    elif dst_agents.exists() and not force_agents:
        print("[跳过] 项目已有 AGENTS.md（如需覆盖加 --force-agents）")
    else:
        shutil.copy2(SRC_AGENTS, dst_agents)
        print("[完成] AGENTS.md -> 项目根")

    print(f"[安装完成] 目标项目：{project}")
    return 1 if (absent or ref_absent or docs_absent) else 0


def check_install(project: Path) -> int:
    """校验目标项目的安装是否完整（skill、模板、参考文档、共享指南均按内容比对）。"""
    skill_dirs = list(iter_skill_dirs(SRC_SKILLS))
    need = False

    for rel in INSTALL_SKILL_DIRS:
        if compare_skills(SRC_SKILLS, project / rel, rel.as_posix()):
            need = True

    if check_template_deps(skill_dirs, project / "templates", "项目 templates/"):
        need = True

    if check_reference_deps(skill_dirs, project / "reference", "项目 reference/"):
        need = True

    if check_docs_deps(skill_dirs, project / "docs", "项目 docs/"):
        need = True

    if check_session_summary_fields(project / "templates", "项目 templates/"):
        need = True

    if not (project / "AGENTS.md").exists():
        print("[提示] 项目缺少 AGENTS.md（跨工具入口）")

    if not need:
        print(f"[一致] 项目安装完整（{len(skill_dirs)} 个 skill + 模板/参考/共享指南，内容与本仓库一致）")
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
