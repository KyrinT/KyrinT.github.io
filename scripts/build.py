#!/usr/bin/env python3
"""将 Markdown 构建成中英双语网站；中文旧地址保持不变，英文位于 en/。"""
from __future__ import annotations
import argparse
from datetime import date, datetime
from html import escape, unescape
from pathlib import Path
import posixpath
import re
import shutil
import sys
from urllib.parse import urlsplit

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import LANGS, UI

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ('学习笔记', '科研记录', '生活随笔')


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


def lang_path(path: str, lang: str) -> str:
    return ('en/' if lang == 'en' else '') + path


def relative_url(target: str, current_path: str) -> str:
    """相对链接兼容根域名、仓库子目录和 file:// 离线预览。"""
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


def render_markdown(source: str, current_path: str, lang: str = 'zh') -> str:
    source = re.sub(r'<!--[\s\S]*?-->', '', source)
    output = markdown.markdown(source, extensions=['extra', 'toc', 'sane_lists', 'pymdownx.arithmatex'],
                               extension_configs={'pymdownx.arithmatex': {'generic': True}})
    def convert(match):
        target = unescape(match[2])
        parts = urlsplit(target)
        # /research.html 等导航自动指向当前语言；/assets/ 始终共享。
        if parts.path in ('/', '/index.html', '/research.html', '/blog.html'):
            page = lang_path(parts.path.lstrip('/') or 'index.html', lang)
            target = '/' + page
            if parts.query:
                target += '?' + parts.query
            if parts.fragment:
                target += '#' + parts.fragment
        return match[1] + escape(relative_url(target, current_path), quote=True) + match[3]
    return re.sub(r'((?:href|src)=")(/(?!/)[^"]*)(")', convert, output)


def load_posts(root: Path) -> list[dict]:
    posts, seen, translation_seen = [], set(), set()
    for path in sorted((root / 'content/posts').glob('*.md')):
        meta, source = read_markdown(path)
        draft = meta.get('draft', True)
        if not isinstance(draft, bool):
            raise ValueError(f'{path.name}: draft 必须为 true 或 false（不加引号）。')
        if draft:
            continue
        title = as_text(meta.get('title', ''), f'{path.name} title')
        category = meta.get('category')
        lang = meta.get('lang', 'zh')
        if lang not in LANGS:
            raise ValueError(f'{path.name}: lang 只能是 zh 或 en。')
        slug = as_text(meta.get('slug', path.stem), f'{path.name} slug')
        key = as_text(meta.get('translation_key', slug), f'{path.name} translation_key')
        if not title:
            raise ValueError(f'{path.name}: 缺少 title。')
        if category not in CATEGORIES:
            raise ValueError(f'{path.name}: category 只能是 {", ".join(CATEGORIES)}。')
        for field, value in [('slug', slug), ('translation_key', key)]:
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value):
                raise ValueError(f'{path.name}: {field} 请使用小写英文字母、数字和单个连字符。')
        if (lang, slug) in seen:
            raise ValueError(f'{path.name}: {lang} 的 slug {slug} 重复。')
        if (lang, key) in translation_seen:
            raise ValueError(f'{path.name}: 同一语言的 translation_key {key} 重复。')
        seen.add((lang, slug))
        translation_seen.add((lang, key))
        when = meta.get('date')
        if isinstance(when, datetime):
            when = when.date()
        if not isinstance(when, date):
            try:
                when = date.fromisoformat(str(when))
            except ValueError as exc:
                raise ValueError(f'{path.name}: date 请使用 YYYY-MM-DD 格式。') from exc
        summary = as_text(meta.get('summary', ''), f'{path.name} summary')
        target = lang_path(f'posts/{slug}.html', lang)
        body = render_markdown(source, target, lang)
        if not summary:
            summary = unescape(re.sub(r'<[^>]*>', '', body)).strip().replace('\n', ' ')[:120]
        posts.append(dict(title=title, category=category, slug=slug, date=when.isoformat(),
                          summary=summary, body=body, path=target, lang=lang, translation_key=key))
    groups = {}
    for post in posts:
        groups.setdefault(post['translation_key'], {})[post['lang']] = post
    for key, variants in groups.items():
        if len({p['category'] for p in variants.values()}) > 1:
            raise ValueError(f'translation_key {key}: 中英文版本的 category 必须相同。')
        for post in variants.values():
            post['alternates'] = {lang: p['path'] for lang, p in variants.items()}
    return sorted(posts, key=lambda p: (p['date'], p['slug']), reverse=True)


def localized_posts(posts: list[dict], lang: str) -> list[dict]:
    groups = {}
    for post in posts:
        groups.setdefault(post['translation_key'], {})[post['lang']] = post
    result = []
    for variants in groups.values():
        # 无译文时展示原文并标注语言；同一篇双语文章只计数一次。
        post = variants.get(lang) or next(iter(variants.values()))
        label = UI[lang]['bilingual'] if len(variants) == 2 else UI[lang]['only_' + post['lang']]
        result.append({**post, 'language_label': label})
    return sorted(result, key=lambda p: (p['date'], p['slug']), reverse=True)


def build(root: Path = ROOT) -> Path:
    root = root.resolve()
    config = yaml.safe_load((root / 'site.yaml').read_text(encoding='utf-8'))
    required = ('title', 'description', 'name', 'bio', 'affiliation', 'location', 'email', 'github', 'scholar', 'avatar', 'cv', 'footer')
    if not isinstance(config, dict):
        raise ValueError('site.yaml 格式错误。')
    sites = {}
    for lang in LANGS:
        combined = dict(config)
        locale_file = root / f'site.{lang}.yaml'
        if locale_file.is_file():
            override = yaml.safe_load(locale_file.read_text(encoding='utf-8')) or {}
            if not isinstance(override, dict):
                raise ValueError(f'{locale_file.name}: 格式错误。')
            combined.update(override)
        site = {key: as_text(combined.get(key, ''), key) for key in required}
        if not site['name'] or not site['title']:
            raise ValueError('name 和 title 不能为空。')
        for key in ('github', 'scholar'):
            if site[key] and urlsplit(site[key]).scheme not in ('http', 'https'):
                raise ValueError(f'{key} 应填写完整的 https:// 地址，或者留空。')
        if not site['avatar']:
            site['avatar'] = 'assets/images/avatar-placeholder.svg'
        sites[lang] = site
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

    def write(path: str, template: str, lang: str, alternates: dict, **context):
        ui, site = UI[lang], sites[lang]
        navigation = [(s, ui[s], lang_path(p, lang)) for s, p in [('home', 'index.html'), ('research', 'research.html'), ('blog', 'blog.html')]]
        values = dict(site=site, ui=ui, lang=lang, alternates=alternates,
                      navigation=navigation, year=date.today().year, description=site['description'],
                      is_post=False, has_math='class="arithmatex"' in context.get('body', ''),
                      url=lambda p: relative_url(p, path), home_path=lang_path('index.html', lang),
                      blog_path=lang_path('blog.html', lang))
        values.update(context)
        destination = output / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(env.get_template(template).render(**values), encoding='utf-8')

    for lang in LANGS:
        source_dir = root / 'content' / ('en' if lang == 'en' else '')
        for section, filename, target, kicker in [('home', 'home.md', 'index.html', 'ABOUT ME'),
                                                  ('research', 'research.md', 'research.html', 'RESEARCH')]:
            meta, content = read_markdown(source_dir / filename)
            path = lang_path(target, lang)
            write(path, 'page.html', lang, {l: lang_path(target, l) for l in LANGS},
                  section=section, title=as_text(meta.get('title', ''), filename + ' title'),
                  kicker=kicker, body=render_markdown(content, path, lang))
        visible_posts = localized_posts(posts, lang)
        counts = {c: sum(p['category'] == c for p in visible_posts) for c in CATEGORIES}
        counts['全部'] = len(visible_posts)
        write(lang_path('blog.html', lang), 'blog.html', lang, {l: lang_path('blog.html', l) for l in LANGS},
              section='blog', title=UI[lang]['blog'], categories=('全部',) + CATEGORIES,
              posts=visible_posts, counts=counts)
    for post in posts:
        write(post['path'], 'post.html', post['lang'], post['alternates'], section='blog', is_post=True,
              title=post['title'], description=post['summary'], body=post['body'], post=post)
    write('404.html', 'page.html', 'zh', {'zh': 'index.html', 'en': 'en/index.html'},
          section='', title=UI['zh']['not_found'], kicker='404', body='<p>' + UI['zh']['not_found_body'] + '</p>')
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
