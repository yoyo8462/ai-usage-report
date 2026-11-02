#!/usr/bin/env python3
"""檢查最近幾天的排程有沒有跑。

比對兩個地方：
- 桌面 App 的排程設定（scheduled-tasks.json）：哪些排程啟用中、cron 哪幾天該跑、App 記下的跳過原因
- ~/.claude/projects 的對話檔：第一則訊息是 <scheduled-task name="..."> 的，就是一次實際執行

只讀不寫。用法：
    python3 check_schedule_runs.py            # 檢查昨天往前 3 天（不含今天）
    python3 check_schedule_runs.py --days 7
    python3 check_schedule_runs.py --date 2026-10-28   # 只檢查某一天
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys
from collections import Counter, defaultdict

HOME = os.path.expanduser("~")
# 桌面 App 存排程設定的位置：Mac 在 ~/Library/Application Support，Windows 在 %APPDATA%
SETTINGS_GLOBS = [
    os.path.join(HOME, "Library", "Application Support", "Claude", "claude-code-sessions", "*", "*",
                 "scheduled-tasks.json"),
    os.path.join(os.environ.get("APPDATA", os.path.join(HOME, "AppData", "Roaming")), "Claude",
                 "claude-code-sessions", "*", "*", "scheduled-tasks.json"),
]
PROJECTS_GLOB = os.path.join(HOME, ".claude", "projects", "*", "*.jsonl")
TZ = dt.datetime.now().astimezone().tzinfo
SKIP_REASON = {"global_limit": "同時執行的排程太多", "per_task_limit": "上一次還沒結束"}


def md(d):
    return "%d/%d" % (d.month, d.day)  # Windows 的 strftime 不支援 %-m


def cron_field_match(field, value, lo, hi):
    """支援 *、*/n、a、a-b、a-b/n、逗號清單。"""
    for part in field.split(","):
        step = 1
        if "/" in part:
            part, s = part.split("/")
            step = int(s)
        if part == "*":
            a, b = lo, hi
        elif "-" in part:
            a, b = (int(x) for x in part.split("-"))
        else:
            a = b = int(part)
        if a <= value <= b and (value - a) % step == 0:
            return True
    return False


def due_on(cron, day):
    """cron 五欄，只看日、月、星期是否落在這一天。"""
    _, _, dom, mon, dow = cron.split()
    cron_dow = (day.isoweekday()) % 7  # 0＝星期日
    ok_dow = cron_field_match(dow, cron_dow, 0, 7) or (cron_dow == 0 and cron_field_match(dow, 7, 0, 7))
    return cron_field_match(dom, day.day, 1, 31) and cron_field_match(mon, day.month, 1, 12) and ok_dow


def load_settings():
    files = sorted((f for g in SETTINGS_GLOBS for f in glob.glob(g)), key=os.path.getmtime)
    if not files:
        raise RuntimeError("找不到桌面 App 的排程設定檔（沒有用排程就會這樣）")
    with open(files[-1], encoding="utf-8") as fh:
        return json.load(fh)


def first_user_text(path):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") != "user":
                continue
            m = d.get("message", {}).get("content")
            if isinstance(m, list):
                m = " ".join(x.get("text", "") for x in m if isinstance(x, dict))
            if isinstance(m, str) and m.strip():
                return d.get("timestamp", ""), m.strip()
    return None, None


def load_runs(since):
    runs = defaultdict(list)  # task -> [local datetime]
    floor = dt.datetime.combine(since, dt.time()).timestamp()
    for p in glob.glob(PROJECTS_GLOB):
        if os.path.getmtime(p) < floor:
            continue
        ts, text = first_user_text(p)
        if not ts or not text.startswith("<scheduled-task"):
            continue
        name = text.split('name="', 1)[1].split('"', 1)[0]
        when = dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ)
        runs[name].append(when)
    return runs


def check(days):
    """回傳 (應跑次數, [(日期, 排程名稱, 跳過原因)])。ai-usage-report 的 collect.py 也呼叫這支。"""
    settings = load_settings()
    tasks = [t for t in settings.get("scheduledTasks", []) if t.get("enabled") and t.get("cronExpression")]
    skips = defaultdict(Counter)  # (task, date) -> reason counts
    for tid, items in (settings.get("recordedSkips") or {}).items():
        for x in items:
            d = dt.datetime.fromtimestamp(x["at"] / 1000, TZ).date()
            skips[(tid, d)][x.get("reason", "unknown")] += 1
    runs = load_runs(days[0])

    missing, checked = [], 0
    for day in days:
        for t in tasks:
            tid = t["id"]
            created = t.get("createdAt")
            if created and dt.datetime.fromtimestamp(created / 1000, TZ).date() > day:
                continue
            if not due_on(t["cronExpression"], day):
                continue
            checked += 1
            if any(r.date() == day for r in runs.get(tid, [])):
                continue
            why = "、".join(SKIP_REASON.get(r, r) for r in skips.get((tid, day), {}))
            missing.append((day, t.get("displayName") or tid, why))
    return checked, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3)
    ap.add_argument("--date")
    args = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    today = dt.date.today()
    if args.date:
        days = [dt.date.fromisoformat(args.date)]
    else:
        days = [today - dt.timedelta(i) for i in range(args.days, 0, -1)]

    try:
        checked, missing = check(days)
    except (OSError, ValueError, RuntimeError) as e:
        print("排程檢查讀取失敗：%s" % e)
        return 0

    span = "%s～%s" % (md(days[0]), md(days[-1]))
    if not missing:
        print("排程：%s 應跑 %d 次，全部有跑。" % (span, checked))
        return 0
    print("⚠ 排程：%s 應跑 %d 次，有 %d 次沒跑。" % (span, checked, len(missing)))
    wk = "一二三四五六日"
    for day, name, why in missing:
        line = "- %s（%s）%s" % (md(day), wk[day.weekday()], name)
        if why:
            line += "：App 記錄跳過，原因是%s" % why
        else:
            line += "：沒有執行紀錄，可能是電腦睡著或 App 沒開"
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
