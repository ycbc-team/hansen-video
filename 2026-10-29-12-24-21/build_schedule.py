# -*- coding: utf-8 -*-
"""按「每2-3天一条、4条一个循环(1爆款+3日常)」生成发布排期表"""
import json, csv, datetime

D = json.load(open("双表.json", encoding="utf-8"))
bao, daily = D["bao"], D["daily"]

# 爆款按 S -> A -> B 排，同级别内保持原顺序
order = {"S": 0, "A": 1, "B": 2}
bao_sorted = sorted(bao, key=lambda r: (order.get(r[1], 9), r[0]))
# 补录/新做条目不按等级排队尾，提前排到近期的爆款位
# 理由：补录＝当下真实发生的行为，素材新鲜、趁热做；按等级排会被推到一年后
# FRESH_GROUPS：每组按顺序连续排进相邻爆款位（组与组之间隔一个爆款位）
FRESH_GROUPS = [
    ["B43"],                    # 10-30 补录：假哭试探
    ["B44"],                    # 10-30 补录：推车搭脚
    ["B18", "B45", "B46"],      # 外出三部曲连发：尖叫鸡 → 出门视察 → 看房睡着
]
# 先把所有组成员取出来（保持原顺序）
claimed = []
for grp in FRESH_GROUPS:
    for gid in grp:
        for r in bao_sorted:
            if r[0] == gid:
                claimed.append(r)
                break
for r in claimed:
    bao_sorted.remove(r)
# 再按组插回：第 gi 组从第 (1+2*gi) 个位置开始，组内成员连续
ci = 0
for gi, grp in enumerate(FRESH_GROUPS):
    pos = 1 + 2 * gi
    for _ in grp:
        bao_sorted.insert(min(pos, len(bao_sorted)), claimed[ci])
        ci += 1
        pos += 1

SEQ = []          # (池类型, 行)
bi = di = 0
while bi < len(bao_sorted) or di < len(daily):
    if bi < len(bao_sorted):
        SEQ.append(("爆款", bao_sorted[bi])); bi += 1
    for _ in range(3):
        if di < len(daily):
            SEQ.append(("日常", daily[di])); di += 1

WD = "一二三四五六日"
start = datetime.date(2026, 11, 1)
cur = start
rows = []
for i, (pool, r) in enumerate(SEQ, 1):
    rows.append({
        "序号": i,
        "计划发布": f"{cur.year}-{cur.month:02d}-{cur.day:02d} 周{WD[cur.weekday()]}",
        "_date": cur,
        "池": pool,
        "编号": r[0],
        "等级": r[1] if pool == "爆款" else "",
        "选题": r[3] if pool == "爆款" else r[2],
        "类型": r[4] if pool == "爆款" else r[3],
        "时长": r[5] if pool == "爆款" else r[4],
        "日记日期": r[2] if pool == "爆款" else r[1],
        "画面要点": r[7] if pool == "爆款" else r[5],
    })
    cur += datetime.timedelta(days=2 if i % 2 else 3)   # 2/3 天交替，均值2.5天

with open("发布排期表.csv", "w", newline="", encoding="utf-8-sig") as f:
    fields = ["序号", "计划发布", "池", "编号", "等级", "选题", "类型", "时长", "日记日期", "画面要点"]
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)

# Markdown：前 8 周 + 每月统计
md = ["# 瀚森投喂日记 · 发布排期表（每2–3天一条）", "",
      f"共 {len(rows)} 条，从 {start.year}年{start.month}月{start.day}日 起排，"
      f"计划排到 {rows[-1]['_date'].year}年{rows[-1]['_date'].month}月{rows[-1]['_date'].day}日。", "",
      "节奏：**4 条一个循环 = 1 条爆款 + 3 条日常**，条与条之间隔 2–3 天（交替）。", "",
      "## 排不下的时候怎么砍", "",
      "- **宁可砍日常，别砍爆款**：日常少发一条只是掉一点权重，爆款错过就浪费了。",
      "- **断更超 7 天，回来第一条先发爆款**，不要用日常重启。",
      "- **提前做好的存着**：一次做完 2 条存 1 条，应对突发。", "",
      "## 前 8 周排期", "",
      "| 序号 | 计划发布 | 池 | 编号 | 选题 | 时长 |", "|---|---|---|---|---|---|"]

end8 = start + datetime.timedelta(days=56)
kept = []
for r in rows:
    if r["_date"] <= end8:
        kept.append(r)
        md.append(f"| {r['序号']} | {r['计划发布']} | {r['池']} | {r['编号']} | {r['选题']} | {r['时长']} |")

md += ["", "## 每月产能与库存", "", "| 月份 | 本月条数 | 其中爆款 | 累计已发 | 爆款池余 | 日常池余 |", "|---|---|---|---|---|---|"]
mb = md_ = 0
bacc = dacc = 0
cur_month = None
for r in rows:
    m = (r["_date"].year, r["_date"].month)
    if cur_month is not None and m != cur_month:
        md.append(f"| {cur_month[0]}年{cur_month[1]}月 | {mb} | {md_} | {bacc+dacc} | {len(bao_sorted)-bacc} | {len(daily)-dacc} |")
        mb = md_ = 0
    cur_month = m
    mb += 1
    if r["池"] == "爆款":
        md_ += 1; bacc += 1
    else:
        dacc += 1
md.append(f"| {cur_month[0]}年{cur_month[1]}月 | {mb} | {md_} | {bacc+dacc} | {len(bao_sorted)-bacc} | {len(daily)-dacc} |")

md += ["", "## 全量排期（167 条）", "",
       "| 序号 | 计划发布 | 池 | 编号 | 选题 | 时长 | 日记日期 |", "|---|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['序号']} | {r['计划发布']} | {r['池']} | {r['编号']} | {r['选题']} | {r['时长']} | {r['日记日期']} |")

open("发布排期表.md", "w", encoding="utf-8").write("\n".join(md) + "\n")

print("总条数", len(rows), "| 爆款", sum(1 for r in rows if r["池"] == "爆款"), "| 日常", sum(1 for r in rows if r["池"] == "日常"))
print("起", rows[0]["计划发布"], "止", rows[-1]["计划发布"], "共", (rows[-1]["_date"]-start).days, "天")
for r in kept[:14]:
    print(r["序号"], r["计划发布"], r["池"], r["编号"], r["选题"])
