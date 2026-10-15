import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

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
        shutil.copy(ROOT / 'site.yaml', self.root / 'site.yaml')
    def tearDown(self):
        self.tmp.cleanup()
    def post(self, filename='sample.md', draft='false', slug='sample', body='正文'):
        (self.root / 'content/posts' / filename).write_text(
            f'---\ntitle: "测试文章"\ndate: 2026-01-01\ncategory: "学习笔记"\nslug: "{slug}"\nsummary: "摘要"\ndraft: {draft}\n---\n\n{body}\n', encoding='utf-8')
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
