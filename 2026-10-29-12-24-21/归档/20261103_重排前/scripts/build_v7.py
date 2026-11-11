# -*- coding: utf-8 -*-
"""生成两件事：
1) 覆盖 爆款池.csv / 日常池.csv 为新口径（原文件已备份到 归档/）
2) 生成 选题重排表.html —— 深色仪表盘，纯 CSS 分页签 + 纯 CSS 弹窗，零 JS（手机端可用）
"""
import json, csv, os
from collections import Counter, OrderedDict

BASE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(BASE, '重排.json'), encoding='utf-8'))
bao, rest = d['bao'], d['rest']

CATS = ['搞怪动作', '成长节点', '家庭关系', '温情']
CAT_C = {'搞怪动作': '#f0883e', '成长节点': '#58a6ff', '家庭关系': '#3fb950', '温情': '#e3b341'}
CAT_D = {
    '搞怪动作': '画面里出现了「不该发生但发生了」的动作。静音也成立，不需要台词。',
    '成长节点': '第一次做到某件事，能力解锁。有明确的「之前不会、现在会了」。',
    '家庭关系': '人物之间的互动张力。需要两个人以上才有戏，靠关系反差。',
    '温情': '情绪落点，治愈向。靠情感共鸣成立，不靠动作。',
}
GD_C = {'S+': '#f85149', 'S': '#f0883e', 'A': '#d29922', 'B': '#58a6ff', 'C': '#6e7681'}
GD_CLS = {'S+': 'sp', 'S': 's', 'A': 'a', 'B': 'b', 'C': 'c'}

# 移出爆款池的（在 rest 里且原属爆款池）
moved = [r for r in rest if r.get('pool') == '爆款池']

# ============ 1. 覆盖 CSV ============
def w(path, header, rows):
    with open(os.path.join(BASE, path), 'w', encoding='utf-8-sig', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(header)
        wr.writerows(rows)

w('爆款池.csv',
  ['编号', '新档位', '原等级', '日期', '选题', '题材类型', '画面强度', '建议时长', '综合分', '为什么能爆', '画面要点'],
  [[r['no'], r['new'], r['old'], r['date'], r['title'], r['cat'], r['vis'], r['dur'], r['score'], r['why'], r['shot']] for r in bao])

w('日常池.csv',
  ['编号', '发布序', '新档位', '原好拍度', '日期', '选题', '题材类型', '画面强度', '建议时长', '综合分', '画面要点'],
  [[r['no'], r['order'], r['new'], r['old'], r['date'], r['title'], r['cat'], r['vis'], r['dur'], r['score'], r['shot']] for r in rest])

print('CSV 覆盖完成：爆款池 %d 行 / 日常池 %d 行' % (len(bao), len(rest)))

# ============ 2. 生成 HTML ============
allitems = [dict(r, seq=i + 1) for i, r in enumerate(bao)]
rest_sorted = sorted(rest, key=lambda r: r['order'])

def gd(v):
    return '<span class="g g-%s">%s</span>' % (GD_CLS.get(v, 'c'), v)

def badge(cat):
    return '<span class="ct" style="color:%s;border-color:%s">%s</span>' % (CAT_C[cat], CAT_C[cat] + '55', cat)

def row(r, rank, show_seq=False):
    no = r['no']
    meta = no
    if show_seq:
        meta += ' · No.%d' % r['seq']
    meta += ' · %s · %s' % (r['date'], r['dur'])
    return (
        '<label class="row" for="i-%s" style="border-left:3px solid %s">'
        '<span class="rk">%d</span>'
        '<span class="bd"><span class="ti">%s</span>'
        '<span class="mt">%s %s</span></span>'
        '<span class="rt">%s<span class="sc">%s</span></span>'
        '</label>'
    ) % (no, CAT_C[r['cat']], rank, r['title'], badge(r['cat']), meta, gd(r['new']), ('%.1f' % r['score']))

def modal(r, note=''):
    no = r['no']
    kv = [
        ('编号', no),
        ('题材类型', r['cat']),
        ('画面强度', r['vis']),
        ('建议时长', r['dur']),
        ('日期出处', r['date']),
        ('综合分', '%.1f' % r['score']),
        ('新档位', r['new']),
        ('原档位', r['old']),
    ]
    if r.get('order'):
        kv.append(('非爆款发布序', '第 %d 位' % r['order']))
    kvh = ''.join('<div class="k"><span>%s</span><b>%s</b></div>' % (k, v) for k, v in kv)
    extra = ''
    if r.get('why'):
        extra += '<div class="blk"><h4>为什么能爆</h4><p>%s</p></div>' % r['why']
    extra += '<div class="blk"><h4>画面要点</h4><p>%s</p></div>' % (r['shot'] or '—')
    if note:
        extra += '<div class="blk"><h4>重评说明</h4><p>%s</p></div>' % note
    return (
        '<div class="modal" id="d-%s">'
        '<label class="mask" for="i-%s"></label>'
        '<div class="sheet">'
        '<div class="s-top">%s<span class="s-sc">%.1f</span><label class="x" for="i-%s">关闭</label></div>'
        '<h3>%s</h3>'
        '<div class="kvs">%s</div>%s'
        '</div></div>'
    ) % (no, no, gd(r['new']), r['score'], no, r['title'], kvh, extra)

# --- 统计 ---
cat_n = Counter(r['cat'] for r in allitems + rest_sorted)
gd_n = Counter(r['new'] for r in allitems + rest_sorted)
top30 = rest_sorted[:30]
top30_cat = Counter(r['cat'] for r in top30)
cat_src = {}
for c in CATS:
    s = [r for r in rest_sorted if r['cat'] == c]
    cat_src[c] = (len(s), round(max([x['score'] for x in s] or [0]), 1), Counter(x['new'] for x in s))

maxn = max(len([r for r in allitems + rest_sorted if r['cat'] == c]) for c in CATS)
bars = ''.join(
    '<div class="brow"><span class="bn2">%s</span>'
    '<span class="bt"><i style="width:%.0f%%;background:%s"></i></span>'
    '<span class="bv">%d</span></div>' % (
        c, len([r for r in allitems + rest_sorted if r['cat'] == c]) / maxn * 100, CAT_C[c],
        len([r for r in allitems + rest_sorted if r['cat'] == c]))
    for c in CATS)

# --- 分页签 ---
TABS = [
    ('t0', '概览', ''),
    ('t1', '爆款池 %d' % len(bao), ''),
    ('t2', '总表 %d' % len(rest_sorted), ''),
    ('t3', '搞怪 %d' % cat_n['搞怪动作'], ''),
    ('t4', '成长 %d' % cat_n['成长节点'], ''),
    ('t5', '家庭 %d' % cat_n['家庭关系'], ''),
    ('t6', '温情 %d' % cat_n['温情'], ''),
    ('t7', '移出 %d' % len(moved), ''),
]

def panel(tid, body):
    return '<section class="panel p-%s">%s</section>' % (tid, body)

# 概览
ov = """
<div class="card">
  <div class="cd-h">这份表是怎么排出来的</div>
  <p>按对标账号「源来是爱」（抖音 68 作品）的实测点赞结构重排。最近 12 条：中位数 <b>2.75 万</b>赞，最高 <b>10.9 万</b>，最低 <b>4337</b>，极差 <b>25 倍</b>；两条超级爆款分别是成长节点（翻身 120.3 万）与搞怪动作（枕头阿贝贝 185.0 万）。</p>
  <p>结论只有一个：<b>搞怪动作向拉高，温情向拉低。</b>垫底三条全是亲情温情向（父子宠妈 4337、相册里的妈妈 9743、倔脾气 1.1 万），登顶三条是动作搞怪向（怪手 10.9 万、源来是热了 9.7 万、隔代亲 6.2 万）。</p>
</div>
<div class="card">
  <div class="cd-h">四类分布</div>
  %s
  <div class="note">前 30 条里，搞怪动作占 <b>%d 条（%d%%）</b>，成长节点 %d、家庭关系 %d、温情 <b>0</b>。温情类最高分只有 7.4，进不了前 30。</div>
</div>
<div class="card">
  <div class="cd-h">四类口径</div>
  <div class="defs">%s</div>
</div>
<div class="card">
  <div class="cd-h">打分公式</div>
  <p class="mono">优先级分 = 类型权重×2 + 画面强度 + 时长分 + 原池分</p>
  <div class="kvlist">
    <div class="k"><span>类型权重</span><b>搞怪动作 3.0 / 成长节点 2.6 / 家庭关系 2.0 / 温情 1.2</b></div>
    <div class="k"><span>画面强度</span><b>强 2.0 / 中 1.0 / 弱 0</b></div>
    <div class="k"><span>时长分</span><b>15–25秒 +1.0 / 25–40秒 +0.3 / 40–55秒 −0.5</b></div>
    <div class="k"><span>原池分</span><b>爆款 S 3.0 / A 2.0 / B 1.0；日常 P0 1.2 / P1 0.5 / P2 0</b></div>
    <div class="k"><span>档位</span><b>S+ ≥11.5 / S ≥10 / A ≥8.5 / B ≥7 / C &lt;7</b></div>
  </div>
</div>
<div class="card warn">
  <div class="cd-h">样本局限（要记住）</div>
  <p>类型权重是从<b>一个账号的 12 条视频</b>推出来的。方向可信——搞怪动作明显高于温情；但 <b>「2 倍还是 4 倍」这种精度不能当结论</b>。等你积累了自己的前 20 条真实数据，这套权重应该重算一遍。</p>
</div>
""" % (bars, top30_cat['搞怪动作'], round(top30_cat['搞怪动作'] / 30 * 100),
       top30_cat['成长节点'], top30_cat['家庭关系'],
       ''.join('<div class="drow"><span class="dot" style="background:%s"></span><b>%s</b><i>%s</i></div>' % (CAT_C[c], c, CAT_D[c]) for c in CATS))

# 表一 爆款池
t1 = '<div class="hd"><h2>表一 · 爆款池 %d 条</h2><p>原 46 条重评后保留 29 条。点任意一条看详情。</p></div>' % len(bao)
t1 += '<div class="list">' + ''.join(row(r, i + 1) for i, r in enumerate(bao)) + '</div>'

# 表二 总表
t2 = '<div class="hd"><h2>表二 · 除爆款外的发布优先级 %d 条</h2><p>全部非爆款选题，按综合分从高到低。</p></div>' % len(rest_sorted)
t2 += '<div class="list">' + ''.join(row(r, r['order']) for r in rest_sorted) + '</div>'

# 四类表
cat_panels = []
tmap = {'搞怪动作': 't3', '成长节点': 't4', '家庭关系': 't5', '温情': 't6'}
for c in CATS:
    s = [r for r in rest_sorted if r['cat'] == c]
    n, mx, dist = cat_src[c]
    dists = ' / '.join('%s %d' % (k, dist[k]) for k in ['S', 'A', 'B', 'C'] if dist[k])
    body = '<div class="hd"><h2>%s %d 条</h2><p>%s</p><p class="sub">最高分 %s · 档位分布：%s</p></div>' % (c, n, CAT_D[c], mx, dists)
    body += '<div class="list">' + ''.join(row(r, i + 1) for i, r in enumerate(s)) + '</div>'
    cat_panels.append((tmap[c], body))

# 表七 移出
t7 = '<div class="hd"><h2>从爆款池移出的 %d 条</h2><p>原标 S/A 但按新口径达不到 A，降入日常池。已在总表中按新分数排序。</p></div>' % len(moved)
t7 += '<div class="list">' + ''.join(row(r, i + 1) for i, r in enumerate(moved)) + '</div>'

panels = [panel('t0', ov), panel('t1', t1), panel('t2', t2)]
for tid, body in cat_panels:
    panels.append(panel(tid, body))
panels.append(panel('t7', t7))

# 输入控件
radios = ''.join('<input type="radio" name="tab" id="%s" class="tin"%s>' % (t[0], ' checked' if i == 0 else '')
                 for i, t in enumerate(TABS))
checks = ''.join('<input type="checkbox" id="i-%s" class="mi">' % r['no'] for r in allitems + rest_sorted)
modals = ''.join(modal(r) for r in allitems + rest_sorted)

navs = ''.join('<label for="%s">%s</label>' % (t[0], t[1]) for t in TABS)

# 分页签 CSS
tab_css = '\n'.join([
    '.tin{display:none}',
    '.panel{display:none}',
] + ['#%s:checked ~ main .p-%s{display:block}\n#%s:checked ~ nav label[for="%s"]{background:#1f6feb;color:#fff;border-color:#1f6feb}' % (tid, tid, tid, tid) for tid, _, _ in TABS])

# 弹窗 CSS（每条约一行）
modal_css = '\n'.join('#i-%s:checked ~ #d-%s{display:flex}' % (r['no'], r['no']) for r in allitems + rest_sorted)

HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>瀚森投喂日记 · 选题重排表</title>
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;background:#0d1117;color:#c9d1d9;font:14px/1.6 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif;padding-bottom:40px}
header{padding:18px 16px 10px;border-bottom:1px solid #21262d}
h1{margin:0 0 6px;font-size:19px;color:#e6edf3;letter-spacing:.3px}
.sub0{margin:0;font-size:12px;color:#8b949e}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.chip{font-size:11px;padding:3px 8px;border-radius:20px;background:#161b22;border:1px solid #30363d;color:#8b949e}
.chip b{color:#e6edf3}
nav{display:flex;flex-wrap:wrap;gap:6px;padding:9px 12px;background:#0d1117;border-bottom:1px solid #21262d;position:sticky;top:0;z-index:20}
nav label{flex:0 0 auto;font-size:12.5px;padding:6px 12px;border-radius:8px;border:1px solid #30363d;background:#161b22;color:#8b949e;cursor:pointer;white-space:nowrap;transition:.15s}
main{padding:14px 12px}
.hd h2{margin:6px 0 4px;font-size:16px;color:#e6edf3}
.hd p{margin:0 0 4px;font-size:12.5px;color:#8b949e}
.hd .sub{color:#6e7681;font-size:12px;margin-bottom:10px}
.list{display:flex;flex-direction:column;gap:6px;margin-top:8px}
.row{display:flex;align-items:center;gap:9px;background:#161b22;border:1px solid #21262d;border-radius:10px;padding:9px 10px 9px 8px;cursor:pointer;transition:.12s}
.row:active{background:#1c2230;border-color:#1f6feb}
.rk{flex:0 0 26px;font-size:12px;color:#6e7681;font-variant-numeric:tabular-nums;text-align:right}
.bd{flex:1;min-width:0;display:flex;flex-direction:column;gap:3px}
.ti{font-size:13.5px;color:#e6edf3;line-height:1.45}
.mt{font-size:11px;color:#6e7681;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.ct{font-size:10.5px;padding:1px 6px;border:1px solid;border-radius:4px;line-height:1.5}
.rt{flex:0 0 auto;display:flex;flex-direction:column;align-items:flex-end;gap:3px}
.sc{font-size:12px;color:#8b949e;font-variant-numeric:tabular-nums}
.g{font-size:11px;font-weight:700;padding:1px 7px;border-radius:5px;color:#0d1117}
.g-sp{background:#f85149}.g-s{background:#f0883e}.g-a{background:#d29922}.g-b{background:#58a6ff}.g-c{background:#6e7681;color:#0d1117}
.card{background:#161b22;border:1px solid #21262d;border-radius:12px;padding:14px;margin-bottom:12px}
.cd-h{font-size:14px;color:#e6edf3;font-weight:700;margin-bottom:8px;padding-left:9px;border-left:3px solid #1f6feb}
.card p{margin:0 0 8px;font-size:13px;color:#a9b4c0}
.card p:last-child{margin-bottom:0}
.card b{color:#e6edf3}
.warn .cd-h{border-left-color:#d29922}
.note{margin-top:10px;font-size:12px;color:#8b949e;border-top:1px dashed #21262d;padding-top:9px}
.brow{display:flex;align-items:center;gap:9px;margin-bottom:7px}
.bn2{flex:0 0 58px;font-size:12px;color:#a9b4c0}
.bt{flex:1;height:15px;background:#0d1117;border-radius:4px;overflow:hidden;border:1px solid #21262d}
.bt i{display:block;height:100%%;border-radius:3px}
.bv{flex:0 0 30px;text-align:right;font-size:12px;color:#e6edf3;font-variant-numeric:tabular-nums}
.defs{display:flex;flex-direction:column;gap:9px}
.drow{display:grid;grid-template-columns:10px 64px 1fr;gap:8px;align-items:start;font-size:12.5px}
.drow b{font-size:12.5px}
.drow i{font-style:normal;color:#8b949e;font-size:12px;line-height:1.5}
.dot{width:8px;height:8px;border-radius:50%%;margin-top:6px}
.kvlist{display:flex;flex-direction:column;gap:7px}
.k{display:flex;gap:10px;font-size:12px;padding:5px 0;border-bottom:1px dashed #21262d}
.k span{flex:0 0 72px;color:#6e7681}
.k b{color:#c9d1d9;font-weight:400}
.mono{font-family:Menlo,monospace;font-size:11.5px;word-break:keep-all;background:#0d1117;border:1px solid #21262d;border-radius:6px;padding:8px;color:#58a6ff!important}
/* 弹窗 */
mi{}
.mi{display:none}
.modal{display:none;position:fixed;inset:0;z-index:100;align-items:center;justify-content:center;padding:16px}
.mask{position:absolute;inset:0;background:rgba(1,4,9,.78);backdrop-filter:blur(2px)}
.sheet{position:relative;width:100%%;max-width:460px;max-height:82vh;overflow-y:auto;background:#161b22;border:1px solid #30363d;border-radius:14px;padding:16px;box-shadow:0 16px 50px rgba(0,0,0,.6);-webkit-overflow-scrolling:touch}
.s-top{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.s-sc{font-size:15px;color:#f0883e;font-weight:700;font-variant-numeric:tabular-nums}
.x{margin-left:auto;font-size:12px;color:#8b949e;border:1px solid #30363d;border-radius:6px;padding:3px 10px;cursor:pointer}
.sheet h3{margin:0 0 12px;font-size:15.5px;color:#e6edf3;line-height:1.45}
.kvs{display:flex;flex-direction:column;gap:0;margin-bottom:12px}
.blk{margin-top:10px;padding-top:10px;border-top:1px solid #21262d}
.blk h4{margin:0 0 5px;font-size:12px;color:#6e7681;font-weight:600}
.blk p{margin:0;font-size:13px;color:#c9d1d9;line-height:1.65}
%s
%s
</style></head>
<body>
%s
%s
<header>
  <h1>瀚森投喂日记 · 选题重排表</h1>
  <p class="sub0">170 条按「搞怪动作 / 成长节点 / 家庭关系 / 温情」重打标，并按对标账号实测数据重算发布优先级</p>
  <div class="chips">
    <span class="chip">总 <b>170</b></span>
    <span class="chip">爆款池 <b>%d</b></span>
    <span class="chip">非爆款 <b>%d</b></span>
    <span class="chip">S+ <b>%d</b></span>
    <span class="chip">S <b>%d</b></span>
    <span class="chip">A <b>%d</b></span>
  </div>
</header>
<nav>%s</nav>
<main>%s</main>
%s
</body></html>""" % (
    tab_css, modal_css,
    radios, checks, len(bao), len(rest_sorted),
    gd_n['S+'], gd_n['S'], gd_n['A'],
    navs,
    ''.join(panels), modals)

out = os.path.join(BASE, '选题重排表.html')
open(out, 'w', encoding='utf-8').write(HTML)
print('HTML 生成：', out, '%.0f KB' % (os.path.getsize(out) / 1024))
print('弹窗条数：', len(allitems + rest_sorted), '| 移出：', len(moved))
print('四类：', dict(cat_n))
print('档位：', dict(gd_n))
