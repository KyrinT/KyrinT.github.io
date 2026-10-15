"""页面界面文本；文章的分类标识保持中文，方便兼容已有文章。"""
LANGS = ('zh', 'en')
UI = {
    'zh': {
        'html_lang': 'zh-CN', 'home': '首页', 'research': '研究', 'blog': '博客',
        'skip': '跳到正文', 'navigation': '主导航', 'language': '切换语言',
        'profile': '个人信息', 'portrait': '的头像', 'email': '邮箱', 'cv': '下载简历 PDF',
        'categories': {'全部': '全部', '学习笔记': '学习笔记', '科研记录': '科研记录', '生活随笔': '生活随笔'},
        'category_label': '文章分类', 'search': '搜索文章', 'search_placeholder': '搜索标题、摘要…',
        'blog_intro': '记录学到的知识、研究中的思考，以及生活里值得留下的片段。',
        'read_more': '阅读全文 →', 'back_blog': '← 返回博客', 'all_posts': '← 查看全部文章',
        'empty_title': '第一篇记录，敬请期待。', 'empty_description': '新的记录将在这里陆续更新。',
        'empty_category': '暂无{category}，敬请期待。', 'no_results': '没有找到相关记录。',
        'try_again': '试试其他关键词，或切换文章分类。',
        'noscript': '当前显示所有文章。启用 JavaScript 后可使用分类和搜索。',
        'only_zh': '仅中文', 'only_en': '仅英文', 'bilingual': '中英双语',
        'unavailable': '本文暂无英文版',
        'guide': [
            ('学习笔记', '课程知识、论文阅读与编程实践，把理解的过程记录下来。'),
            ('科研记录', '研究问题、方法探索与阶段思考，记录每一点进展。'),
            ('生活随笔', '日常生活、旅行、阅读与感想，收藏学术之外的片段。')
        ],
        'not_found': '没有找到这个页面', 'not_found_body': '页面可能已移动，请从顶部导航返回首页或博客。'
    },
    'en': {
        'html_lang': 'en', 'home': 'Home', 'research': 'Research', 'blog': 'Blog',
        'skip': 'Skip to content', 'navigation': 'Main navigation', 'language': 'Select language',
        'profile': 'Profile', 'portrait': "'s portrait", 'email': 'Email', 'cv': 'Download CV (PDF)',
        'categories': {'全部': 'All', '学习笔记': 'Study Notes', '科研记录': 'Research Notes', '生活随笔': 'Life & Reflections'},
        'category_label': 'Post categories', 'search': 'Search posts', 'search_placeholder': 'Search titles, summaries…',
        'blog_intro': 'Notes on learning, reflections on research, and moments worth keeping.',
        'read_more': 'Read more →', 'back_blog': '← Back to blog', 'all_posts': '← View all posts',
        'empty_title': 'The first post is on its way.', 'empty_description': 'New posts will appear here.',
        'empty_category': 'No posts in {category} yet.', 'no_results': 'No matching posts.',
        'try_again': 'Try another keyword or category.',
        'noscript': 'All posts are shown. Enable JavaScript to filter and search.',
        'only_zh': 'Chinese only', 'only_en': 'English only', 'bilingual': '中文 / English',
        'unavailable': 'This post is not yet available in Chinese.',
        'guide': [
            ('Study Notes', 'Coursework, paper reading, and programming: recording the process of understanding.'),
            ('Research Notes', 'Questions, methods, and reflections: documenting progress along the way.'),
            ('Life & Reflections', 'Everyday life, travel, reading, and thoughts beyond research.')
        ],
        'not_found': 'Page not found', 'not_found_body': 'This page may have moved. Use the navigation to return to Home or Blog.'
    }
}
