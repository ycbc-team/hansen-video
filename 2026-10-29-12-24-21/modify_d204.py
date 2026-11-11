# -*- coding: utf-8 -*-
"""D204 改归温情，提至 A 档（与 D203 逻辑一致）。"""
import json, os
BASE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(BASE, '重排.json')
d = json.load(open(P, encoding='utf-8'))
rest = d['rest']
# 温情公式：2.8 + 中1.0 + 15-25s1.0 + P1 0.17 + 温情共鸣0.6 = 5.57 -> A
for r in rest:
    if r['no'] == 'D204':
        r['cat'] = '温情'
        r['score'] = 5.57
        r['new'] = 'A'
        r['note'] = ('v9 补录：洗衣机/泡奶机/吹风机滴滴声→停下玩具、眼睛循声、开始思考。'
                     '听觉敏感期+因果认知。改归温情(情感共鸣强)，与 D203 逻辑一致，提至 A 档。')
        print('D204 updated -> cat=温情, score=5.57, new=A')
        break
else:
    print('D204 NOT FOUND')
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('saved 重排.json')
