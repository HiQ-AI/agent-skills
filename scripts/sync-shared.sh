#!/usr/bin/env bash
# 把 skills/_shared/cortex.py 同步进每个技能包的 scripts/。
#
# 各技能包共用同一个 HTTP client,唯一真实来源是 skills/_shared/cortex.py。
# 生成物必须入库 —— `npx skills add HiQ-AI/agent-skills --skill <name>` 直接从
# 仓库目录安装,包里没有脚本就跑不起来。
#
# 改完 client 跑一次本脚本,再 git add 全部技能包。
set -euo pipefail

cd "$(dirname "$0")/.."
src="skills/_shared/cortex.py"

[ -f "$src" ] || { echo "缺少 $src" >&2; exit 1; }

# 只同步「已经在用这个 client」的包 —— 有些技能不走 cortex.py(如 hiq-editor 用
# npx @hiq-ai/hiq-editor),给它们塞一个用不上的脚本只会让包变大、让人误以为要跑它。
for skill in skills/*/; do
  name="$(basename "$skill")"
  [ "$name" = "_shared" ] && continue
  [ -f "$skill/SKILL.md" ] || continue
  [ -f "$skill/scripts/cortex.py" ] || { echo "跳过 $name(不使用 cortex.py)"; continue; }
  cp "$src" "$skill/scripts/cortex.py"
  echo "→ $skill/scripts/cortex.py"
done
