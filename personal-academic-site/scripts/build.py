#!/usr/bin/env python3
"""把 site.yaml、content 中的 Markdown 与 templates 合成为 _site 静态网页。"""
from __future__ import annotations
import argparse
from datetime import date, datetime
from html import escape
from pathlib import Path
import posixpath
import re
import shutil
from urllib.parse import urlsplit

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ('学习笔记', '科研记录', '生活随笔')
NAVIGATION = (('home', '首页', 'index.html'), ('research', '研究', 'research.html'), ('blog', '博客', 'blog.html'))


def read_markdown(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding='utf-8-sig')
    match = re.match(r'\A---\s*\n(.*?)\n---\s*\n(.*)\Z', raw, re.S)
    if not match:
        raise ValueError(f'{path.name}: 文件顶部需要 --- 包围的标题等信息。')
    data = yaml.safe_load(match[1]) or {}
    if not isinstance(data, dict):
        raise ValueError(f'{path.name}: 顶部信息必须是键值对。')
    return data, match[2]


def as_text(value, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f'{name}: 请使用文本，必要时加双引号。')
    return value.strip()


def relative_url(target: str, current_path: str) -> str:
    """所有内部路径转换为相对路径：用户主页、子目录和离线预览通用。"""
    if target.startswith('//') or urlsplit(target).scheme or target.startswith('#'):
        return target
    parts = urlsplit(target)
    dest = parts.path.lstrip('/') or 'index.html'
    result = posixpath.relpath(dest, posixpath.dirname(current_path) or '.')
    if parts.query:
        result += '?' + parts.query
    if parts.fragment:
        result += '#' + parts.fragment
    return result


def render_markdown(source: str, current_path: str) -> str:
    # HTML 注释只是作者提示，不放入公开的网页源码。
    source = re.sub(r'<!--[\s\S]*?-->', '', source)
    output = markdown.markdown(source, extensions=['extra', 'toc', 'sane_lists', 'pymdownx.arithmatex'],
                               extension_configs={'pymdownx.arithmatex': {'generic': True}})
    # 文中以 /assets/... 或 /blog.html 开头的路径按当前页面位置转换。
    def convert(match):
        return match[1] + escape(relative_url(match[2], current_path), quote=True) + match[3]
    return re.sub(r'((?:href|src)=")(/(?!/)[^"]*)(")', convert, output)


def load_posts(root: Path) -> list[dict]:
    posts = []
    seen = set()
    for path in sorted((root / 'content/posts').glob('*.md')):
        meta, source = read_markdown(path)
        draft = meta.get('draft', True)
        if not isinstance(draft, bool):
            raise ValueError(f'{path.name}: draft 必须为 true 或 false（不加引号）。')
        if draft:
            continue
        title = as_text(meta.get('title', ''), f'{path.name} title')
        category = meta.get('category')
        slug = as_text(meta.get('slug', path.stem), f'{path.name} slug')
        if not title:
            raise ValueError(f'{path.name}: 缺少 title。')
        if category not in CATEGORIES:
            raise ValueError(f'{path.name}: category 只能是 {", ".join(CATEGORIES)}。')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            raise ValueError(f'{path.name}: slug 请使用小写英文字母、数字和单个连字符。')
        if slug in seen:
            raise ValueError(f'{path.name}: slug {slug} 重复，请为每篇文章使用独立地址。')
        seen.add(slug)
        when = meta.get('date')
        if isinstance(when, datetime):
            when = when.date()
        if not isinstance(when, date):
            try:
                when = date.fromisoformat(str(when))
            except ValueError as exc:
                raise ValueError(f'{path.name}: date 请使用 YYYY-MM-DD 格式。') from exc
        summary = as_text(meta.get('summary', ''), f'{path.name} summary')
        target = f'posts/{slug}.html'
        body = render_markdown(source, target)
        if not summary:
            summary = re.sub(r'<[^>]*>', '', body).strip().replace('\n', ' ')[:120]
        posts.append(dict(title=title, category=category, slug=slug, date=when.isoformat(),
                          summary=summary, body=body, path=target))
    return sorted(posts, key=lambda p: (p['date'], p['slug']), reverse=True)


def build(root: Path = ROOT) -> Path:
    root = root.resolve()
    config = yaml.safe_load((root / 'site.yaml').read_text(encoding='utf-8'))
    required = ('title', 'description', 'name', 'bio', 'affiliation', 'location', 'email', 'github', 'scholar', 'avatar', 'cv', 'footer')
    if not isinstance(config, dict):
        raise ValueError('site.yaml 格式错误。')
    site = {key: as_text(config.get(key, ''), key) for key in required}
    if not site['name'] or not site['title']:
        raise ValueError('site.yaml 中的 name 和 title 不能为空。')
    for key in ('github', 'scholar'):
        if site[key] and urlsplit(site[key]).scheme not in ('http', 'https'):
            raise ValueError(f'site.yaml 的 {key} 应填写完整的 https:// 地址，或者留空。')
    if not site['avatar']:
        site['avatar'] = 'assets/images/avatar-placeholder.svg'
    posts = load_posts(root)
    env = Environment(loader=FileSystemLoader(root / 'templates'), autoescape=select_autoescape(['html']),
                      undefined=StrictUndefined)
    output = root / '_site'
    if output.is_symlink():
        raise ValueError('_site 不可为符号链接。')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    shutil.copytree(root / 'assets', output / 'assets', ignore=shutil.ignore_patterns('.gitkeep', '.DS_Store'))
    (output / '.nojekyll').touch()

    def write(path: str, template: str, **context):
        body = context.get('body', '')
        values = dict(site=site, navigation=NAVIGATION, year=date.today().year,
                      description=site['description'], is_post=False,
                      has_math='class="arithmatex"' in body,
                      url=lambda p: relative_url(p, path))
        values.update(context)
        destination = output / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(env.get_template(template).render(**values), encoding='utf-8')

    for section, source, target, kicker in [('home', 'home.md', 'index.html', 'ABOUT ME'),
                                          ('research', 'research.md', 'research.html', 'RESEARCH')]:
        meta, content = read_markdown(root / 'content' / source)
        write(target, 'page.html', section=section, title=as_text(meta.get('title', ''), source + ' title'),
              kicker=kicker, body=render_markdown(content, target))
    counts = {c: sum(p['category'] == c for p in posts) for c in CATEGORIES}
    counts['全部'] = len(posts)
    write('blog.html', 'blog.html', section='blog', title='博客', categories=('全部',) + CATEGORIES,
          posts=posts, counts=counts)
    for post in posts:
        write(post['path'], 'post.html', section='blog', is_post=True, title=post['title'],
              description=post['summary'], body=post['body'], post=post)
    write('404.html', 'page.html', section='', title='没有找到这个页面', kicker='404',
          body='<p>页面可能已移动，请从顶部导航返回首页或博客。</p>')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        destination = build(args.root)
        print(f'构建完成：{destination}')
    except (ValueError, yaml.YAMLError) as exc:
        raise SystemExit(f'构建失败：{exc}')
