# 个人学术主页：研究、学习与生活

这是可以下载到本地、通过 Git 管理、由 GitHub Pages 自动发布的完整网站项目。
布局参考 Academic Pages：左侧个人信息，顶部三个独立页面，右侧正文。

- **首页**：自我介绍、研究兴趣、教育经历、获奖经历。
- **研究**：近期研究方向、发表论文（当前为空）。
- **博客**：学习笔记、科研记录、生活随笔。每篇文章有独立网址，支持分类和搜索。
- 支持 Markdown、图片、表格、代码块、`$…$` 行内公式与 `$$…$$` 独立公式。
- 采用 Python 构建静态网页，GitHub Actions 自动构建与发布；日常修改只需要编辑内容文件。

**双语版本：** 顶部可切换中文与 English，日常维护方法见 [双语版本使用说明.md](双语版本使用说明.md)。英文使用 Times New Roman，中文优先使用楷体。

**首次上线请先看 [开始使用.md](开始使用.md)。**

## 我平时改什么？

| 要修改的内容 | 文件或目录 |
|---|---|
| 姓名、邮箱、头像与账号链接等共用信息 | `site.yaml` |
| 中文 / 英文侧栏文字、网站标题 | `site.zh.yaml` / `site.en.yaml` |
| 首页介绍、研究兴趣、教育和获奖经历 | `content/home.md` |
| 研究方向、论文列表 | `content/research.md` |
| 英文首页 / 英文研究页 | `content/en/home.md` / `content/en/research.md` |
| 博客文章 | `content/posts/`，每种语言一个 `.md` 文件 |
| 图片与头像 | `assets/images/` |
| 简历和论文 PDF | `assets/files/` |
| 三种文章模板 | `examples/` |
| 配色、字体、间距 | `assets/css/style.css` |
| 网页结构 | `templates/` |
| 自动发布流程 | `.github/workflows/deploy.yml` |

`_site/` 是构建生成的网页，不是平时编辑的内容。压缩包中附有初始预览；Git 会忽略这个目录，GitHub 会重新生成它。

## 发布一篇博客

1. 从 `examples/` 复制一个模板到 `content/posts/`。
2. 文件名使用英文，例如 `2026-10-15-first-note.md`。
3. 修改文件顶部的信息，写好正文。
4. 将 `draft: true` 改为 `draft: false`。
5. 提交并推送到 GitHub 的 `main` 分支。

```yaml
---
title: "我的第一篇学习笔记"
date: 2026-10-15
category: "学习笔记"
slug: "first-learning-note"
summary: "这篇文章讲了什么。"
draft: false
---
```

在第二个 `---` 下面写 Markdown 正文即可。

- `category` 只能填：`学习笔记`、`科研记录`、`生活随笔`。
- `slug` 决定文章的网址，例如 `posts/first-learning-note.html`。使用小写英文字母、数字和连字符，同一语言内每篇不同，中英文译文可用相同 slug；发布后尽量不要改，否则旧链接会失效。
- `date` 控制显示日期与排序；本项目不根据未来日期定时发布。`draft: false` 的文章在下次成功部署时就会上线。
- `draft: true` 的文章不会进入网站。未写 `draft` 也按草稿处理。
- 公开仓库中的源文件本身仍然可见；不想公开的私人草稿请留在仓库外。
- 修改已发布文章：修改原文件，提交并推送。
- 删除文章：删除对应 `.md` 文件，提交并推送；成功部署后页面和列表会一起移除。

## 图片、PDF、链接

将图片放进 `assets/images/`。建议使用英文短文件名，避免空格。

```markdown
![照片的文字描述](/assets/images/my-photo.jpg)

[下载论文](/assets/files/paper.pdf)

[查看研究](/research.html)

[外部链接](https://example.com)
```

以 `/assets/` 开头的链接会自动转换成正确的相对地址；无论网站位于 `用户名.github.io` 还是 `用户名.github.io/仓库名/` 都可以使用。

从 Obsidian 导出时，图片使用上面的标准 Markdown 语法；`![[图片.jpg]]` 和 `[[双链]]` 需要改成标准图片和链接语法。附件图片也要一并复制到 `assets/images/`。

## 数学公式

```markdown
行内公式：$E = mc^2$。

独立公式（前后留空行）：

$$
\Delta W_{ij} = -\eta \frac{\partial L}{\partial W_{ij}}
$$
```

含公式的页面使用 MathJax 渲染。MathJax 从 CDN 加载，首次查看公式需要能连接该服务；普通文字、样式和图片由网站自身提供。

## 本地查看（可选）

首次下载后，可以直接双击 `_site/index.html` 查看初始页面，导航可以切换。它是打包时的预览，修改 Markdown 后不会自己变化。

只需要在线更新时，**不必在本机安装 Python 依赖**。直接编辑内容、推送，由 GitHub 自动构建即可。

需要在本地预览新修改时，安装 Python 3.10 或更新版本，在项目目录运行：

**macOS / Linux：**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/check_site.py
python -m http.server 8000 --directory _site
```

**Windows PowerShell：**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/build.py
.\.venv\Scripts\python.exe scripts/check_site.py
.\.venv\Scripts\python.exe -m http.server 8000 --directory _site
```

浏览器打开 <http://localhost:8000>。结束时按 `Ctrl+C`。

后续改完内容，再执行一次 `python scripts/build.py`，然后刷新浏览器。这里没有自动监控本地改动；可以用第二个终端构建，也可以先停止预览再构建。

## 以后每次更新

```bash
git add .
git commit -m "更新网站内容"
git push
```

在 GitHub 仓库的 **Actions** 页面查看发布状态。只有构建和发布均成功，线上网站才更新；失败时之前成功发布的版本仍然可访问。

如果也在 GitHub 网页改过文件，开始本地编辑前先运行 `git pull --ff-only`。如果出现冲突，不要强制覆盖，可把报错发给协助者。

## 网站地址

- 仓库名为 `你的用户名.github.io`：`https://你的用户名.github.io/`。
- 普通仓库名如 `personal-site`：`https://你的用户名.github.io/personal-site/`。

本项目使用相对链接，两种地址均支持；不用在源文件中手动写入用户名或仓库路径。

网站文件属于你的仓库，可以自己修改，也可以把有关文件和报错发给我继续协助。此前的 Sites 网页是独立网站，不会自动跟随这个 GitHub 仓库同步；新网站发布后请分享 GitHub Pages 的网址。

## 技术结构

`scripts/build.py` 使用 Markdown、PyMdown Extensions 和 Jinja2，把 `site.yaml`、`content/` 与 `templates/` 生成到 `_site/`。GitHub 的官方 Pages Actions 上传并部署 `_site/`，不需要配置个人访问令牌。

`tests/` 验证草稿排除、删除文章后的清理、文章独立路径、数学公式保留与分类约束；`scripts/check_site.py` 检查生成网页引用的本地图片和文件是否存在。

自动发布只上传 `_site/`，不把 README、测试或构建脚本作为网页发布。

## 参考文档

- [GitHub Pages 发布源设置](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [GitHub Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Python-Markdown](https://python-markdown.github.io/)
- [PyMdown Arithmatex 数学公式](https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/)
- [布局参考 Academic Pages](https://academicpages.github.io/)
