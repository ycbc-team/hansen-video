# -*- coding: utf-8 -*-
"""把 4 个选题缺口补录进 重排.json（rest 总表），按 v9 公式实算 score 与档位。"""
import json, os
BASE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(BASE, '重排.json')
d = json.load(open(P, encoding='utf-8'))
bao, rest = d['bao'], d['rest']

print('补录前: 爆款池 %d / 总表 %d' % (len(bao), len(rest)))
max_order = max(r['order'] for r in rest)
print('总表 max order =', max_order)

TYPE = {'家长博弈':3.3,'家庭关系':3.0,'科学育儿梗':2.9,'温情':2.8,'成长节点':2.8,'搞怪动作':2.4}
VIS  = {'强':2.0,'中':1.0,'弱':0.0}
DUR  = {'15–25秒':1.0,'25–40秒':0.3,'40–55秒':-0.5}
ORIG = {'S':1.0,'A':0.67,'B':0.33,'P0':0.40,'P1':0.17,'P2':0.0}
RES  = {'家庭关系':0.6,'温情':0.6,'家长博弈':0.3,'成长节点':0.3,'科学育儿梗':0.2,'搞怪动作':0.0}

def score_of(cat, vis, dur, old, attach, pen):
    return round(TYPE[cat] + VIS[vis] + DUR[dur] + ORIG[old] + RES[cat] + attach + pen, 2)

def grade(s):
    if s >= 6.5: return 'S+'
    if s >= 6.0: return 'S'
    if s >= 5.5: return 'A'
    if s >= 4.6: return 'B'
    return 'C'

gaps = [
  dict(no='D201', orig_pool='日常池', old='P1', date='11月补录',
       title='打疫苗后嗜睡，叫都叫不醒',
       cat='科学育儿梗', vis='中', dur='15–25秒',
       shot='打完疫苗一路睡，到家叫都叫不醒',
       why='疫苗后嗜睡反差，区别于排队困/扎针睡',
       attach=0.0, pen=0.0,
       note='v9 补录：区别于 D35「排队打疫苗困到上课睡觉」(排队时困)、D08「针戳哭两下继续睡」(扎针时睡)，本条是「打完疫苗后嗜睡、叫不醒」精确版。'),
  dict(no='D202', orig_pool='日常池', old='P1', date='11月补录',
       title='爱看洗衣机转转的样子',
       cat='成长节点', vis='中', dur='15–25秒',
       shot='盯着洗衣机滚筒转，看得出神',
       why='专注力/认知萌芽，第一次对运转物体着迷',
       attach=0.0, pen=0.0,
       note='v9 补录：专注力/认知萌芽，第一次对运转物体着迷。'),
  dict(no='D203', orig_pool='日常池', old='P1', date='11月补录',
       title='爱看阿姨打扫，头跟着转',
       cat='温情', vis='中', dur='15–25秒',
       shot='阿姨扫地拖地到哪，娃的头就转到哪',
       why='治愈向，娃看阿姨干活头跟着转，情感共鸣强',
       attach=0.0, pen=0.0,
       note='v9 补录：归温情(情感共鸣强)。若改成长节点则降为 B 档。'),
  dict(no='D204', orig_pool='日常池', old='P1', date='11月补录',
       title='娃的谨慎日常：听到滴滴声就停下玩具循声看',
       cat='科学育儿梗', vis='中', dur='15–25秒',
       shot='洗衣机/泡奶机/吹风机滴滴响，娃停玩具、眼睛循声、开始思考',
       why='听觉敏感期+因果认知，谨慎观察',
       attach=0.0, pen=0.0,
       note='v9 补录：洗衣机/泡奶机/吹风机滴滴声→停下玩具、眼睛循声、开始思考。听觉敏感期+因果认知。'),
]

for i, g in enumerate(gaps):
    sc = score_of(g['cat'], g['vis'], g['dur'], g['old'], g['attach'], g['pen'])
    g['score'] = sc
    g['new'] = grade(sc)
    g['order'] = max_order + 1 + i
    g['pool'] = '日常池'
    g['promo'] = False
    g['demote'] = False
    rest.append(g)
    print('  + %s | %s | %s | score=%.2f | %s | order=%d' % (g['no'], g['title'], g['cat'], sc, g['new'], g['order']))

json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('已写入 重排.json -> 爆款池 %d / 总表 %d' % (len(bao), len(rest)))
