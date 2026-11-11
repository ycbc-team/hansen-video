# -*- coding: utf-8 -*-
"""从 重排.json（v9 六类重打标 + v9 权重）生成文档友好版 HTML，
用于 overwrite_doc_with_html 推送到腾讯文档「选题重排表」。
风格对齐历史 重排表_doc.html：浅色、内联样式、真实表格（Word 可渲染）。
"""
import json, os
from collections import Counter, OrderedDict

BASE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(BASE, '重排.json'), encoding='utf-8'))
bao, rest = d['bao'], d['rest']

CATS = ['家长博弈', '科学育儿梗', '家庭关系', '成长节点', '温情', '搞怪动作']
CAT_D = {
    '家长博弈': '家长和宝宝互相试探、演戏、斗智斗勇。有对抗、有反转，笑点在「大人 vs 宝宝」之间。',
    '科学育儿梗': '专业育儿名词 × 宝宝配合或崩坏。标题里有一个专业词（抬头/抚触/前庭/疫苗/早教）。',
    '家庭关系': '人物之间的互动张力。需要两个人以上才有戏，靠关系反差。',
    '成长节点': '第一次做到某件事，能力解锁。有明确的「之前不会、现在会了」。',
    '温情': '情绪落点，治愈向。靠情感共鸣成立，不靠动作。',
    '搞怪动作': '画面里出现了「不该发生但发生了」的动作。静音也成立，不需要台词。',
}
GD_ORDER = ['S+', 'S', 'A', 'B', 'C']

# 统计
bao_n = len(bao)
rest_n = len(rest)
gd_n = Counter(r['new'] for r in bao)
cat_n = Counter(r['cat'] for r in bao + rest)
moved = [r for r in rest if r.get('orig_pool') == '爆款池']
promoted = [r for r in bao if r.get('promo')]
core_cats = ['家长博弈', '家庭关系', '成长节点', '温情', '科学育儿梗']
core_n = sum(cat_n.get(c, 0) for c in core_cats)

def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

def th(cols):
    return '<tr>' + ''.join("<th style='background:#eee;text-align:left'>%s</th>" % esc(c) for c in cols) + '</tr>'

def row(cells):
    return '<tr>' + ''.join('<td>%s</td>' % esc(c) for c in cells) + '</tr>'

TABLE_OPEN = "<table border='1' cellspacing='0' cellpadding='4' style='border-collapse:collapse;font-size:9pt;width:100%'>"

parts = []
parts.append("<div style=\"font-family:'Microsoft YaHei',sans-serif;font-size:10.5pt;line-height:1.6\">")
parts.append("<h1 style='font-size:20pt'>陪阿森长大 · 选题重排表（v9 六类重打标）</h1>")
parts.append("<p>共 <b>%d</b> 条：<b>爆款池 %d</b> + 其余 %d。依据从「一个账号 73 作品」扩到四个账号全量读数（源来是爱 73 / 又又号 72 / 可可很认可 51 / 仲颗小石榴 39），结论收敛为：关系/温情/成长是天花板，家长博弈是最强单点，搞怪是稳定基本盘。</p>" % (bao_n + rest_n, bao_n, rest_n))
parts.append("<p>爆款池档位分布：S+ %d / S %d / A %d / B %d / C %d。天花板型（博弈+关系+成长+温情+育儿梗）合计 <b>%d 条（%d%%）</b>。从日常池提升 %d 条、从原爆款池降级 %d 条。</p>" % (
    gd_n.get('S+', 0), gd_n.get('S', 0), gd_n.get('A', 0), gd_n.get('B', 0), gd_n.get('C', 0),
    core_n, round(core_n / bao_n * 100), len(promoted), len(moved)))

# 六类口径
parts.append("<h2 style='font-size:15pt'>六类口径</h2>")
parts.append(TABLE_OPEN + th(['分类', '定义', '判断标准']))
for c in CATS:
    parts.append(row([c, CAT_D[c].split('。')[0] + '。', CAT_D[c].split('。', 1)[1] if '。' in CAT_D[c] else '']))
parts.append("</table>")

# 打分公式
parts.append("<h2 style='font-size:15pt'>打分公式（v9，满分约 8.1）</h2>")
parts.append("<p><code>优先级分 = 类型权重 + 画面强度 + 时长分 + 原池分÷3 + 情感共鸣分 + 依恋加分 + 负面扣分</code></p>")
parts.append(TABLE_OPEN + th(['维度', '取值']))
parts.append(row(['类型权重', '家长博弈 3.3 / 家庭关系 3.0 / 科学育儿梗 2.9 / 温情 2.8 / 成长节点 2.8 / 搞怪动作 2.4']))
parts.append(row(['画面强度', '强 2.0 / 中 1.0 / 弱 0']))
parts.append(row(['时长分', '15–25秒 +1.0 / 25–40秒 +0.3 / 40–55秒 −0.5']))
parts.append(row(['原池分÷3', '爆款 S 1.0 / A 0.67 / B 0.33；日常 P0 0.40 / P1 0.17 / P2 0']))
parts.append(row(['情感共鸣分', '家庭关系 +0.6 / 温情 +0.6 / 博弈 +0.3 / 成长 +0.3 / 育儿梗 +0.2 / 搞怪 0']))
parts.append(row(['依恋加分', '分离焦虑/认人/找妈妈 +0.4～0.5（10 条）']))
parts.append(row(['负面扣分', '节日集锦 −0.8 / 节日框架 −0.3（2 条）']))
parts.append(row(['档位', 'S+ ≥6.5 / S ≥6.0 / A ≥5.5 / B ≥4.6 / C &lt;4.6']))
parts.append("</table>")
parts.append("<p>&gt; 说明：权重是四个账号的观察值，方向可信、具体倍数不能当硬结论；等你积累前 20 条真实数据应重算。</p>")

# 表一 爆款池
parts.append("<p>---</p>")
parts.append("<h2 style='font-size:15pt'>表一 · 爆款池（%d 条）</h2>" % bao_n)
parts.append("<p>按综合分从高到低。点看详情请在本地深色仪表盘「选题重排表.html」。</p>")
parts.append(TABLE_OPEN + th(['序', '编号', '六类', '重评', '日期', '选题', '时长', '强度', '分']))
for i, r in enumerate(bao):
    parts.append(row([i + 1, r['no'], r['cat'], r['new'], r.get('date', '—'), r['title'], r['dur'], r['vis'], '%.1f' % r['score']]))
parts.append("</table>")

# 表二 总表（其余）
rest_sorted = sorted(rest, key=lambda r: (-r.get('score', 0), r['order']))
rank = {r['no']: i for i, r in enumerate(rest_sorted, 1)}
parts.append("<p>---</p>")
parts.append("<h2 style='font-size:15pt'>表二 · 除爆款外 · 发布优先级总表（%d 条）</h2>" % rest_n)
parts.append("<p>按综合分从高到低。前 30 条建议作为首批产能。</p>")
parts.append(TABLE_OPEN + th(['序', '编号', '六类', '档', '日期', '选题', '分', '时长', '强度', '备注']))
for i, r in enumerate(rest_sorted, 1):
    note = ''
    if r.get('attach'):
        note = '依恋+%.1f' % r['attach']
    if r.get('pen'):
        note = (note + ' ' if note else '') + '扣%.1f' % r['pen']
    parts.append(row([i, r['no'], r['cat'], r['new'], r.get('date', '—'), r['title'], '%.1f' % r['score'], r['dur'], r['vis'], note]))
parts.append("</table>")

# 六类分表
for c in CATS:
    s = [r for r in rest_sorted if r['cat'] == c]
    n = len(s)
    mx = max([x['score'] for x in s]) if s else 0
    parts.append("<p>---</p>")
    parts.append("<h2 style='font-size:15pt'>表 · %s（%d 条，最高 %.1f）</h2>" % (c, n, mx))
    parts.append(TABLE_OPEN + th(['组内序', '编号', '档', '日期', '选题', '分', '时长', '强度', '总名次']))
    for j, r in enumerate(s):
        parts.append(row([j + 1, r['no'], r['new'], r.get('date', '—'), r['title'], '%.1f' % r['score'], r['dur'], r['vis'], rank[r['no']]]))
    parts.append("</table>")

# 附录 移出
parts.append("<p>---</p>")
parts.append("<h2 style='font-size:15pt'>附录 · 从爆款池移出的 %d 条</h2>" % len(moved))
parts.append(TABLE_OPEN + th(['编号', '六类', '新档', '分', '选题']))
for r in moved:
    parts.append(row([r['no'], r['cat'], r['new'], '%.1f' % r['score'], r['title']]))
parts.append("</table>")

parts.append("</div>")

out = os.path.join(BASE, '选题重排表_doc_v9.html')
open(out, 'w', encoding='utf-8').write(''.join(parts))
print('生成：', out, '%.0f KB' % (os.path.getsize(out) / 1024))
print('爆款池 %d / 其余 %d / 移出 %d / 提升 %d' % (bao_n, rest_n, len(moved), len(promoted)))
print('六类：', dict(cat_n))
print('档位：', dict(gd_n))
