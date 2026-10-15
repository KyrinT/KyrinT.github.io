#!/usr/bin/env python3
"""检查生成网页的本地文件引用，及时发现缺图、缺 PDF 和失效文章链接。"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys

ROOT = Path(__file__).resolve().parents[1] / '_site'

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('href', 'src') and value:
                self.targets.append(value)

def check(root=ROOT):
    errors = []
    for page in root.rglob('*.html'):
        parser = Links()
        parser.feed(page.read_text(encoding='utf-8'))
        for target in parser.targets:
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            path = unquote(parts.path)
            file = (root / path.lstrip('/')) if path.startswith('/') else (page.parent / path)
            if file.is_dir():
                file /= 'index.html'
            if not file.is_file():
                errors.append(f'{page.relative_to(root)} → {target}')
    return errors

if __name__ == '__main__':
    if not ROOT.is_dir():
        sys.exit('请先运行 python scripts/build.py。')
    errors = check()
    if errors:
        sys.exit('发现无效站内链接：\n' + '\n'.join(errors))
    print('检查通过：所有页面、图片和本地文件链接均存在。')
