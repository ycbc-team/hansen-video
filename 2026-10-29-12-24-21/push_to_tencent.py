# -*- coding: utf-8 -*-
"""把本地 HTML 整篇覆盖到腾讯文档（doc-mcp overwrite_doc_with_html）。"""
import base64, json, subprocess, sys, os

SKILL_DIR = "/Users/bettychan/.workbuddy/plugins/cache/workbuddy-builtin/tencent-docs-plugin/5.9.3-wb.42398134.gd4692421.h1dfe572c384a/skills/tencent-docs"
TENC = os.path.join(SKILL_DIR, "tencentdocs.py")

def push(file_id, html_path):
    html = open(html_path, encoding='utf-8').read()
    b64 = base64.b64encode(html.encode('utf-8')).decode('ascii')
    args = {"file_id": file_id, "base64_html_text": b64}
    cmd = ["python3", TENC, "tdoc_call", "doc-mcp", "overwrite_doc_with_html", json.dumps(args, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    print("=== push %s -> %s ===" % (os.path.basename(html_path), file_id))
    out = (r.stdout or "") + (r.stderr or "")
    # 只打印前 800 字符，避免 base64 刷屏
    print(out[:800])
    return r.returncode == 0 and '"error"' not in out.lower()

if __name__ == '__main__':
    fid, path = sys.argv[1], sys.argv[2]
    ok = push(fid, path)
    print("RESULT:", "OK" if ok else "FAIL")
    sys.exit(0 if ok else 1)
