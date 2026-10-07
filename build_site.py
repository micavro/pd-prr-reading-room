"""Build a portable static reading library from explicitly selected sources."""
import hashlib
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
DATA = json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))
MATH_RE = re.compile(r'\\\(.*?\\\)|\\\[.*?\\\]', re.S)
expressions = sorted(set(MATH_RE.findall(json.dumps(DATA, ensure_ascii=False).replace('\\\\', '\\').replace('\\n', '\n'))))
result = subprocess.run(['node', str(ROOT / 'render_math.mjs')], input=json.dumps(expressions), capture_output=True, text=True, encoding='utf-8', check=True)
MATH = json.loads(result.stdout)


def esc(value):
    return html.escape(str(value), quote=True)


def rich_text(value):
    pieces = []
    for paragraph in value.split('\n\n'):
        output = []
        last = 0
        for match in MATH_RE.finditer(paragraph):
            output.append(esc(paragraph[last:match.start()]))
            output.append(MATH[match.group()])
            last = match.end()
        output.append(esc(paragraph[last:]))
        rendered = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', ''.join(output))
        pieces.append('<p>' + rendered + '</p>')
    return ''.join(pieces)


def shell(title, body, prefix='', description='P/D 系列与 PRR 的中文 PDF 和论文阅读问答。'):
    icon = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E%3Crect width=%2232%22 height=%2232%22 rx=%226%22 fill=%22%2311233f%22/%3E%3Cpath d=%22M8 7h7v18H8zm10 0h6v18h-6z%22 fill=%22%23f6c665%22/%3E%3C/svg%3E'
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#11233f"><meta name="description" content="{esc(description)}"><title>{esc(title)} · 论文阅读室</title><link rel="icon" type="image/svg+xml" href="{icon}"><link rel="stylesheet" href="{prefix}assets/style.css"></head>
<body><a class="skip" href="#main">跳到正文</a><header class="top"><div class="top-inner"><a class="brand" href="{prefix}index.html">论文阅读室<small>P/D &amp; PRR</small></a><div class="edition">中文全文 · 论文六问<br>更新于 {esc(DATA['updated'])}</div></div></header>
<main id="main">{body}</main><footer><div class="foot"><div>问答由助手依据论文整理，采用常见论文阅读问题；不是 Kimi 服务的实际输出。</div><div>Safari 中打开 PDF 后，可通过分享菜单保存到“文件”或“图书”。</div></div></footer></body></html>'''


def main():
    (DIST / 'assets').mkdir(parents=True, exist_ok=True)
    (DIST / 'pdfs').mkdir(exist_ok=True)
    (DIST / 'papers').mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'assets/style.css', DIST / 'assets/style.css')
    (DIST / '.nojekyll').write_text('', encoding='utf-8')
    manifest = []
    for paper in DATA['papers']:
        source = (ROOT / paper['pdf_source']).resolve()
        if 'manonly' in source.name.lower():
            raise ValueError('Protected file is not a publication source')
        with fitz.open(source) as pdf:
            paper['pages'] = len(pdf)
            text = ''.join(page.get_text() for page in pdf)
        chinese = sum('\u4e00' <= c <= '\u9fff' for c in text)
        if chinese < 100:
            raise ValueError(f"No usable Chinese translation: {paper['id']}")
        paper['size'] = f'{source.stat().st_size / (1024 * 1024):.1f} MB'
        target = DIST / 'pdfs' / f"{paper['id']}-zh.pdf"
        shutil.copy2(source, target)
        record = {'id': paper['id'], 'pages': paper['pages'], 'bytes': target.stat().st_size,
                  'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'chinese_characters': chinese}
        if paper.get('original_source'):
            original = (ROOT / paper['original_source']).resolve()
            shutil.copy2(original, DIST / 'pdfs' / f"{paper['id']}-en.pdf")
        manifest.append(record)

    nav = ''.join(f'<a href="#{g["id"]}">{esc(g["title"])}<span>{sum(p["group"] == g["id"] for p in DATA["papers"])} 篇</span></a>' for g in DATA['groups'])
    body = f'<div class="intro"><div><h1>从这里开始阅读</h1><p class="description">两组论文，中文全文与逐篇问答。</p></div><div class="count"><strong>{len(DATA["papers"])}</strong>篇论文</div></div><nav class="group-nav" aria-label="论文分组">{nav}</nav>'
    for i, group in enumerate(DATA['groups'], 1):
        papers = [p for p in DATA['papers'] if p['group'] == group['id']]
        body += f'<section class="group" id="{group["id"]}" aria-labelledby="heading-{group["id"]}"><div class="group-head"><span class="group-no">0{i}</span><div><h2 id="heading-{group["id"]}">{esc(group["title"])}</h2><p class="muted">{esc(group["description"])} · {len(papers)} 篇</p></div></div><div class="paper-list">'
        if group.get('scope_note'):
            body += f'<p class="fine">{esc(group["scope_note"])}</p>'
        current_topic = None
        for paper in papers:
            pid = paper['id']
            if paper.get('topic') and paper['topic'] != current_topic:
                current_topic = paper['topic']
                body += f'<h3 class="topic">{esc(current_topic)}</h3>'
            body += f'''<article class="paper {group['id']}"><div><div class="meta"><span class="code">{esc(paper['short'])}</span><span>{esc(paper['venue'])}</span><span>中文 {paper['pages']} 页 · {paper['size']}</span></div><h3><a href="papers/{pid}.html">{esc(paper['zh_title'])}</a></h3><div class="en-title" lang="en">{esc(paper['title'])}</div><p>{esc(paper['summary'])}</p></div><div class="actions"><a class="button primary" href="pdfs/{pid}-zh.pdf" target="_blank" rel="noopener" aria-label="阅读 {esc(paper['short'])} 中文 PDF（新标签页）">阅读中文 PDF</a><a class="button" href="papers/{pid}.html">论文六问</a></div></article>'''
        body += '</div></section>'
    (DIST / 'index.html').write_text(shell('P/D 与 PRR', body), encoding='utf-8')

    for paper in DATA['papers']:
        pid = paper['id']
        group = next(g for g in DATA['groups'] if g['id'] == paper['group'])
        original = f'<a class="button" href="../pdfs/{pid}-en.pdf" target="_blank" rel="noopener">英文原文</a>' if paper.get('original_source') else ''
        body = f'''<a class="back" href="../index.html#{paper['group']}">返回 {esc(group['title'])} 目录</a><article><header class="paper-header"><div class="meta"><span class="code">{esc(paper['short'])}</span><span>{esc(paper['venue'])}</span><span>中文 {paper['pages']} 页 · {paper['size']}</span></div><h1>{esc(paper['zh_title'])}</h1><div class="en-title" lang="en">{esc(paper['title'])}</div><p class="summary">{esc(paper['summary'])}</p><div class="actions"><a class="button primary" href="../pdfs/{pid}-zh.pdf" target="_blank" rel="noopener">阅读中文 PDF</a>{original}<a class="button" href="{esc(paper['source_url'])}" target="_blank" rel="noopener">论文来源</a></div><p class="fine">{esc(paper['translation_note'])}</p></header><div class="reading"><section aria-labelledby="questions"><h2 id="questions">论文六问</h2><p class="fine">{esc(paper['qa_provenance'])}</p><div class="qa-list">'''
        for i, qa in enumerate(paper['questions'], 1):
            opening = ' open' if i == 1 else ''
            body += f'<details id="q{i}"{opening}><summary>{i:02d} · {esc(qa["q"])}</summary><div class="answer">{rich_text(qa["a"])}<p class="ref">依据：{esc(qa["ref"])}</p></div></details>'
        body += '</div>'
        if paper.get('cautions'):
            body += '<aside class="note" aria-label="阅读校核"><strong>阅读时留意</strong>' + ''.join(rich_text(c) for c in paper['cautions']) + '</aside>'
        body += '</section><aside class="side"><h2>阅读导航</h2><ul class="mini-list">'
        for i, qa in enumerate(paper['questions'], 1):
            body += f'<li><a href="#q{i}">{i:02d} · {esc(qa["q"])}</a></li>'
        body += '</ul><p>先看研究问题，再按需展开方法、实验与研究启发。每个答案附来源定位，便于回到全文核对。</p></aside></div></article>'
        (DIST / 'papers' / f'{pid}.html').write_text(shell(paper['short'], body, '../', paper['summary']), encoding='utf-8')
    (DIST / 'pdf-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'papers': len(manifest), 'pdf_bytes': sum(r['bytes'] for r in manifest), 'directory': str(DIST)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
