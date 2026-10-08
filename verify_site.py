"""Verify the published set, links, PDF integrity, and required content."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = []
        self.summary_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'summary':
            self.summary_count += 1


def main():
    data = json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))
    ids = [paper['id'] for paper in data['papers']]
    assert len(ids) == len(set(ids)), 'Duplicate paper ID'
    for group in data['groups']:
        assert any(p['group'] == group['id'] for p in data['papers']), f"Empty group: {group['id']}"
    parsed = {}
    for path in DIST.rglob('*.html'):
        parser = Links()
        text = path.read_text(encoding='utf-8')
        assert '\ufffd' not in text and 'file://' not in text
        parser.feed(text)
        assert len(parser.ids) == len(set(parser.ids)), f'Duplicate HTML IDs: {path}'
        parsed[path.resolve()] = parser
    for path, parser in parsed.items():
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            assert target.is_relative_to(DIST.resolve()), f'Escaping link: {link}'
            assert target.is_file(), f'Missing link: {path.name}: {link}'
            if url.fragment and target.suffix == '.html':
                assert unquote(url.fragment) in parsed[target].ids, f'Missing anchor: {link}'
    records = json.loads((DIST / 'pdf-manifest.json').read_text())
    assert {record['id'] for record in records} == set(ids), 'Manifest and library differ'
    for record in records:
        target = DIST / 'pdfs' / f"{record['id']}-zh.pdf"
        assert target.read_bytes().startswith(b'%PDF-')
        assert hashlib.sha256(target.read_bytes()).hexdigest() == record['sha256']
        resources = record.get('supplements', []) + ([record['original']] if 'original' in record else [])
        for resource in resources:
            target = (DIST / resource['path']).resolve()
            assert target.is_relative_to(DIST.resolve()), resource['path']
            blob = target.read_bytes()
            assert len(blob) == resource['bytes'], resource['path']
            assert hashlib.sha256(blob).hexdigest() == resource['sha256'], resource['path']
            if target.suffix == '.pdf':
                assert blob.startswith(b'%PDF-'), resource['path']
    for paper in data['papers']:
        assert len(paper['questions']) == 6, paper['id']
        assert parsed[(DIST / 'papers' / f"{paper['id']}.html").resolve()].summary_count == 6
        paper_links = parsed[(DIST / 'papers' / f"{paper['id']}.html").resolve()].links
        record = next(record for record in records if record['id'] == paper['id'])
        if paper.get('original_source'):
            assert record['original']['path'] == f"pdfs/{paper['id']}-en.pdf"
            assert '../' + record['original']['path'] in paper_links
        for supplement in paper.get('supplements', []):
            assert any(item['path'] == supplement['path'] for item in record.get('supplements', []))
            assert '../' + supplement['path'] in paper_links
    print(f"PASS: {len(ids)} papers, {len(parsed)} HTML pages, six answers per paper, all local links and PDF hashes.")


if __name__ == '__main__':
    main()
