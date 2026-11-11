#!/usr/bin/env bash
# 发布到 SkillHub(WorkBuddy)。SkillHub 有频控:逐个发、发完等一会儿、被限流就退避。
#
# hiq-cortex-en 不在这里 —— 英文版走 ClawHub / npx skills 那条线,slug 也是那边的
# `hiq-cortex`,发到 SkillHub 只会撞上被企业账号占死的同名 slug。
cd "$(dirname "$0")/.."
CL="数据查询改用 Environmental Data CLI(environmental-data / epd-data),移除旧 hiq-cortex CLI 与 Cortex MCP 接入;去掉已下线的队列分布、百分位与 EPD 同类分布能力"
SKIP="hiq-cortex-en"
# 断在中间时把已发的名字塞进 PUBLISHED 再跑,不用从头来
DONE="${PUBLISHED:-}"

for d in skills/*/; do
  n=$(basename "$d")
  [ -f "$d/SKILL.md" ] || continue
  case " $SKIP $DONE " in *" $n "*) echo "skip $n"; continue ;; esac

  for attempt in 1 2 3; do
    out=$(python3 ~/.skillhub/skills_store_cli.py publish "$d" --changelog "$CL" 2>&1 | tail -1)
    if echo "$out" | grep -q "Published"; then echo "$n: $out"; sleep 45; break; fi
    echo "$n: attempt $attempt — $out"
    sleep 90
  done
done
echo "=== 全部结束 ==="
