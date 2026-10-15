import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT / 'scripts/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class BuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for folder in ('content', 'templates', 'assets'):
            shutil.copytree(ROOT / folder, self.root / folder)
        # 测试独立于用户之后增加的文章。
        for p in (self.root / 'content/posts').glob('*.md'):
            p.unlink()
        for config in ROOT.glob('site*.yaml'):
            shutil.copy(config, self.root / config.name)
    def tearDown(self):
        self.tmp.cleanup()
    def post(self, filename='sample.md', draft='false', slug='sample', body='正文'):
        (self.root / 'content/posts' / filename).write_text(
            f'---\ntitle: "测试文章"\ndate: 2026-01-01\ncategory: "学习笔记"\nslug: "{slug}"\nsummary: "摘要"\ndraft: {draft}\n---\n\n{body}\n', encoding='utf-8')
    def translated_post(self, filename, lang, slug, key='paired', draft=False, category='学习笔记'):
        meta = dict(title='A study note' if lang == 'en' else '一篇学习笔记',
                    date='2026-10-15', category=category, slug=slug, lang=lang,
                    translation_key=key, summary='Summary' if lang == 'en' else '摘要', draft=draft)
        body = '[Research](/research.html)\n\n![portrait](/assets/images/Myphoto.jpg)\n\n$x^2$'
        (self.root / 'content/posts' / filename).write_text(
            '---\n' + yaml.safe_dump(meta, allow_unicode=True) + '---\n\n' + body, encoding='utf-8')
    def test_bilingual_pages_keep_profile_and_localize_navigation(self):
        out = builder.build(self.root)
        zh = (out / 'index.html').read_text()
        en = (out / 'en/index.html').read_text()
        self.assertIn('<html lang="zh-CN">', zh)
        self.assertIn('<html lang="en">', en)
        self.assertIn('href="en/index.html"', zh)
        self.assertIn('href="../index.html"', en)
        self.assertIn('href="research.html"', en)
        self.assertNotIn('href="../research.html"', en)
        self.assertIn('src="../assets/images/Myphoto.jpg"', en)
        self.assertIn('href="../assets/files/CV.pdf"', en)
        self.assertIn('Shanghai Jiao Tong University', en)
        self.assertIn('上海交通大学', zh)
        self.assertIn('Search titles, summaries', (out / 'en/blog.html').read_text())
    def test_translation_pair_links_and_count(self):
        self.translated_post('note-zh.md', 'zh', 'chinese-note')
        self.translated_post('note-en.md', 'en', 'english-note')
        out = builder.build(self.root)
        zh = (out / 'posts/chinese-note.html').read_text()
        en = (out / 'en/posts/english-note.html').read_text()
        self.assertIn('href="../en/posts/english-note.html"', zh)
        self.assertIn('href="../../posts/chinese-note.html"', en)
        self.assertIn('href="../research.html"', en)
        self.assertIn('href="../blog.html"', en)
        self.assertIn('src="../../assets/images/Myphoto.jpg"', en)
        self.assertIn('src="../../assets/js/math.js"', en)
        self.assertNotIn('lang-unavailable', en)
        for path in ['blog.html', 'en/blog.html']:
            listing = (out / path).read_text()
            self.assertEqual(listing.count('<article class="post-card"'), 1)
            self.assertIn('class="count">1</span>', listing)
        checker_spec = importlib.util.spec_from_file_location('checker', ROOT / 'scripts/check_site.py')
        checker = importlib.util.module_from_spec(checker_spec)
        checker_spec.loader.exec_module(checker)
        self.assertEqual(checker.check(out), [])
    def test_untranslated_legacy_posts_and_draft_translation(self):
        self.post()
        self.translated_post('sample-en.md', 'en', 'sample', key='sample', draft=True)
        out = builder.build(self.root)
        listing = (out / 'en/blog.html').read_text()
        self.assertIn('Chinese only', listing)
        self.assertIn('href="../posts/sample.html"', listing)
        self.assertFalse((out / 'en/posts/sample.html').exists())
        zh = (out / 'posts/sample.html').read_text()
        self.assertIn('本文暂无英文版', zh)
        self.assertIn('aria-disabled="true"', zh)
        self.assertNotIn('hreflang="en"', zh)
    def test_same_slug_in_two_languages_and_english_only_fallback(self):
        self.translated_post('en.md', 'en', 'paired')
        out = builder.build(self.root)
        self.assertIn('仅英文', (out / 'blog.html').read_text())
        self.assertIn('href="en/posts/paired.html"', (out / 'blog.html').read_text())
        self.assertFalse((out / 'posts/paired.html').exists())
        self.translated_post('zh.md', 'zh', 'paired')
        out = builder.build(self.root)
        self.assertTrue((out / 'posts/paired.html').exists())
        self.assertTrue((out / 'en/posts/paired.html').exists())
    def test_ambiguous_translations_fail_with_clear_error(self):
        self.translated_post('one.md', 'en', 'one')
        self.translated_post('two.md', 'en', 'two')
        with self.assertRaisesRegex(ValueError, 'translation_key.*重复'):
            builder.build(self.root)
        self.translated_post('two.md', 'zh', 'two', category='生活随笔')
        with self.assertRaisesRegex(ValueError, 'category 必须相同'):
            builder.build(self.root)
    def test_drafts_stay_out_of_output_and_old_posts_removed(self):
        self.post()
        out = builder.build(self.root)
        self.assertTrue((out / 'posts/sample.html').exists())
        self.post(draft='true')
        builder.build(self.root)
        self.assertFalse((out / 'posts/sample.html').exists())
        self.assertNotIn('测试文章', (out / 'blog.html').read_text())
    def test_post_math_images_and_nested_navigation(self):
        self.post(body=r'行内 $x_i^2$。' + '\n\n$$\n' + r'W_{ij} = \frac{1}{N}\sum_k x_i^k x_j^k' + '\n$$\n\n![头像](/assets/images/avatar-placeholder.svg)')
        out = builder.build(self.root)
        html = (out / 'posts/sample.html').read_text()
        self.assertIn('class="arithmatex"', html)
        self.assertIn(r'\frac{1}{N}', html)
        self.assertIn('href="../index.html"', html)
        self.assertIn('src="../assets/images/avatar-placeholder.svg"', html)
        self.assertIn('MathJax', (out / 'assets/js/math.js').read_text())
        self.assertIn('posts/sample.html', (out / 'blog.html').read_text())
    def test_duplicate_slug_and_invalid_category_fail(self):
        self.post()
        self.post(filename='second.md')
        with self.assertRaisesRegex(ValueError, '重复'):
            builder.build(self.root)
        (self.root / 'content/posts/second.md').unlink()
        file = self.root / 'content/posts/sample.md'
        file.write_text(file.read_text().replace('学习笔记','拼写错误'))
        with self.assertRaisesRegex(ValueError, 'category'):
            builder.build(self.root)
    def test_root_and_repository_subpath_share_same_relative_links(self):
        self.assertEqual(builder.relative_url('/assets/a.png','posts/p.html'), '../assets/a.png')
        self.assertEqual(builder.relative_url('/research.html','index.html'), 'research.html')
        self.assertEqual(builder.relative_url('https://example.com','posts/p.html'), 'https://example.com')

if __name__ == '__main__':
    unittest.main()
