# -*- coding: utf-8 -*-
"""按「选题重排表 v9」新口径（爆款 55 + 其余 116）重排发布节奏。

节奏：每 2–3 天一条；3 条一个循环 = 1 条爆款 + 2 条日常。
理由：v9 爆款池 55（新增家长博弈/科学育儿梗两类、依恋加分、A 及以上全部进池），
     爆款:日常 ≈ 1:2.1，1+2 能让爆款均匀铺满全程；若沿用 1+4，
     日常会在中段耗尽、末尾连排爆款，变成「爆款扎堆」。
补录条目 B43 / B44 / B47 仍提前到第 2、3、4 个爆款位：素材新鲜、趁热做。
"""
import json, csv, datetime
from collections import Counter

D = json.load(open("重排.json", encoding="utf-8"))
bao = D["bao"][:]                     # 已按分数降序
rest = sorted(D["rest"], key=lambda r: r["order"])

# 补录条目提前：B43 第 2 位、B44 第 3 位、B47 第 4 位
HOIST = ["B43", "B44", "B47"]
for k, gid in enumerate(HOIST):
    hit = [r for r in bao if r["no"] == gid]
    if hit:
        bao.remove(hit[0])
        bao.insert(1 + k, hit[0])

CYCLE = (1, 2)          # 1 爆款 + 2 日常
SEQ = []
bi = di = 0
while bi < len(bao) or di < len(rest):
    if bi < len(bao):
        SEQ.append(("爆款", bao[bi])); bi += 1
    for _ in range(CYCLE[1]):
        if di < len(rest):
            SEQ.append(("日常", rest[di])); di += 1

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
        "编号": r["no"],
        "档": r["new"],
        "分": r["score"],
        "四类": r["cat"],
        "选题": r["title"],
        "时长": r["dur"],
        "强度": r["vis"],
        "日记日期": r["date"],
        "画面要点": r["shot"],
    })
    cur += datetime.timedelta(days=2 if i % 2 else 3)

with open("发布排期表.csv", "w", newline="", encoding="utf-8-sig") as f:
    fields = ["序号", "计划发布", "池", "编号", "档", "分", "四类", "选题", "时长", "强度", "日记日期", "画面要点"]
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)

nb = sum(1 for r in rows if r["池"] == "爆款")
last = rows[-1]["_date"]
md = ["# 瀚森投喂日记 · 发布排期表（每 2–3 天一条）", "",
      f"共 {len(rows)} 条，从 {start.year}年{start.month}月{start.day}日 起排，"
      f"计划排到 {last.year}年{last.month}月{last.day}日。", "",
      f"节奏：**3 条一个循环 = 1 条爆款 + 2 条日常**，条与条之间隔 2–3 天（交替），均值 2.5 天，"
      f"爆款约每 7–8 天一条。爆款池 {nb} 条、其余池 {len(rows)-nb} 条。", "",
      f"> 为什么是 1+2 而不是 1+4：v9 爆款池 {nb} 条、日常池 {len(rows)-nb} 条，"
      f"比例约 1:{len(rows)/nb-1:.1f}。按 1+2 排能让爆款均匀铺满全程；"
      "若沿用 1+4，日常会先耗尽、末尾连排爆款。", "",
      "## 排不下的时候怎么砍", "",
      "- **宁可砍日常，别砍爆款**：日常少发一条只是掉一点权重，爆款错过就浪费了。",
      "- **断更超 7 天，回来第一条先发爆款**，不要用日常重启。",
      "- **提前做好的存着**：一次做完 2 条存 1 条，应对突发。",
      "- **爆款爆了就停**：某条数据明显跑赢，暂停按表走，立刻补 2–3 条同类。", "",
      "## 前 8 周排期", "",
      "| 序号 | 计划发布 | 池 | 编号 | 档 | 分 | 选题 | 时长 |", "|---|---|---|---|---|---|---|---|"]

end8 = start + datetime.timedelta(days=56)
kept = [r for r in rows if r["_date"] <= end8]
for r in kept:
    md.append(f"| {r['序号']} | {r['计划发布']} | {r['池']} | {r['编号']} | {r['档']} | {r['分']} | {r['选题']} | {r['时长']} |")

md += ["", "## 每月产能与库存", "",
       "| 月份 | 本月条数 | 其中爆款 | 累计已发 | 爆款池余 | 其余池余 |", "|---|---|---|---|---|---|"]
mb = mb_b = bacc = dacc = 0
cur_month = None
for r in rows:
    m = (r["_date"].year, r["_date"].month)
    if cur_month is not None and m != cur_month:
        md.append(f"| {cur_month[0]}年{cur_month[1]}月 | {mb} | {mb_b} | {bacc+dacc} | {nb-bacc} | {len(rows)-nb-dacc} |")
        mb = mb_b = 0
    cur_month = m
    mb += 1
    if r["池"] == "爆款":
        mb_b += 1; bacc += 1
    else:
        dacc += 1
md.append(f"| {cur_month[0]}年{cur_month[1]}月 | {mb} | {mb_b} | {bacc+dacc} | {nb-bacc} | {len(rows)-nb-dacc} |")

md += ["", f"## 全量排期（{len(rows)} 条）", "",
       "| 序号 | 计划发布 | 池 | 编号 | 档 | 分 | 四类 | 选题 | 时长 | 日记日期 |",
       "|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['序号']} | {r['计划发布']} | {r['池']} | {r['编号']} | {r['档']} | {r['分']} | "
              f"{r['四类']} | {r['选题']} | {r['时长']} | {r['日记日期']} |")

open("发布排期表.md", "w", encoding="utf-8").write("\n".join(md) + "\n")

print("总条数", len(rows), "| 爆款", nb, "| 日常", len(rows) - nb)
print("起", rows[0]["计划发布"], "止", rows[-1]["计划发布"], "共", (rows[-1]["_date"] - start).days, "天")
print("爆款档:", Counter(r["档"] for r in rows if r["池"] == "爆款"))
for r in kept[:12]:
    print(r["序号"], r["计划发布"], r["池"], r["编号"], r["档"], r["选题"][:18])
