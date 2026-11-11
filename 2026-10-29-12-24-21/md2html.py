# -*- coding: utf-8 -*-
"""极简 Markdown -> HTML（仅覆盖本项目用到的语法：标题/表格/代码块/粗体/段落）"""
import re, sys, html

def md2html(md: str) -> str:
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1; continue
        # 代码块
        if s.startswith("```"):
            i += 1; buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(html.escape(lines[i])); i += 1
            i += 1
            out.append("<pre style='background:#f5f5f5;padding:8px;font-family:Menlo;font-size:9pt'>"
                       + "<br/>".join(buf) + "</pre>")
            continue
        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            lv = len(m.group(1))
            size = {1: 20, 2: 15, 3: 13, 4: 12}[lv]
            out.append(f"<h{lv} style='font-size:{size}pt'>{inline(m.group(2))}</h{lv}>")
            i += 1; continue
        # 表格
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1].strip()):
            header = [c.strip() for c in s.strip("|").split("|")]
            i += 2; body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            t = ["<table border='1' cellspacing='0' cellpadding='4' style='border-collapse:collapse;font-size:9pt;width:100%'>",
                 "<tr>" + "".join(f"<th style='background:#eee;text-align:left'>{inline(h)}</th>" for h in header) + "</tr>"]
            for r in body:
                r = (r + [""] * len(header))[:len(header)]
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</table>")
            out.append("".join(t))
            continue
        # 列表
        if re.match(r"^[-*]\s+", s):
            buf = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                buf.append("<li>" + inline(re.sub(r"^[-*]\s+", "", lines[i].strip())) + "</li>"); i += 1
            out.append("<ul>" + "".join(buf) + "</ul>")
            continue
        # 有序列表
        if re.match(r"^\d+\.\s+", s):
            buf = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                buf.append("<li>" + inline(re.sub(r"^\d+\.\s+", "", lines[i].strip())) + "</li>"); i += 1
            out.append("<ol>" + "".join(buf) + "</ol>")
            continue
        # 段落
        out.append("<p>" + inline(s) + "</p>")
        i += 1
    return "<div style=\"font-family:'Microsoft YaHei',sans-serif;font-size:10.5pt;line-height:1.6\">" + "\n".join(out) + "</div>"

def inline(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    open(dst, "w", encoding="utf-8").write(md2html(open(src, encoding="utf-8").read()))
    print("ok", dst)
