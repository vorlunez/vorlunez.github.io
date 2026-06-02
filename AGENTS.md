<!-- From: /Users/zbw/mypro/blog/AGENTS.md -->
# AGENTS.md

本文件面向 AI 编码助手，用于快速了解本项目的技术栈、架构与开发规范。

---

## 项目概述

本项目是一个**极简的个人博客**，使用 Python + Flask 构建，同时支持**纯静态站点生成**以部署到 GitHub Pages。

核心特点：
- **双模式运行**：本地用 Flask 预览，部署时运行 `build.py` 生成纯静态 HTML
- 纯静态文件驱动：将 `.md` 文件放入 `posts/` 目录即可发布文章
- 支持 YAML frontmatter 设置标题、日期、标签
- 支持 Markdown 语法、代码高亮、自动生成目录（TOC）
- 无外部数据库依赖

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask 3.0.3（仅本地开发预览）|
| 静态生成 | `build.py`（Jinja2 + Python-Markdown）|
| Markdown 渲染 | Python-Markdown 3.6（含 fenced_code、tables、codehilite、toc 扩展）|
| 代码高亮 | Pygments 2.18.0 |
| 模板引擎 | Jinja2 |
| 前端样式 | 原生 CSS（无 JS 框架）|
| 字体 | Google Fonts: Noto Serif SC / Noto Sans SC |

---

## 项目结构

```
.
├── app.py              # Flask 应用入口（本地开发服务器）
├── build.py            # 静态站点生成器（部署到 GitHub Pages 前运行）
├── requirements.txt    # Python 依赖
├── start.sh            # 一键启动本地开发服务器
├── posts/              # 文章目录，存放 Markdown 文件
│   └── YYYY-MM-DD-标题.md
├── templates/          # Jinja2 模板
│   ├── base.html       # 基础布局
│   ├── index.html      # 首页：文章列表
│   ├── post.html       # 文章详情页（含 TOC、正文、返回链接）
│   └── about.html      # 关于页面
├── static/
│   └── style.css       # 完整样式表（响应式、Markdown 渲染样式、代码高亮）
│
# 以下由 build.py 自动生成（部署到 GitHub Pages 所需）
├── index.html
├── .nojekyll
├── about/
│   └── index.html
└── post/
    └── <slug>/
        └── index.html
```

> **注意**：`build.py` 生成的 `index.html`、`about/index.html`、`post/*/index.html` 等文件必须一并提交到 GitHub 仓库的 `main` 分支，GitHub Pages 才能正确访问。

---

## 运行方式

### 本地开发预览（Flask）

```bash
./start.sh
```

或手动：

```bash
pip install -r requirements.txt
python app.py
```

本地访问：`http://localhost:5000`

### 生成静态站点（GitHub Pages 部署）

```bash
python build.py
```

生成完成后，将变更 `git add` + `git commit` + `git push` 到 `main` 分支即可。

---

## GitHub Pages 部署说明

### 为什么需要 build.py

`vorlunez.github.io` 是 **GitHub Pages 用户站点**，它只能托管**纯静态文件**（HTML/CSS/JS），**不支持 Python/Flask 后端运行**。因此必须把模板渲染成静态 HTML 后上传。

### 部署步骤

1. 写文章：将 `.md` 文件放入 `posts/` 目录
2. 生成静态文件：
   ```bash
   python3 build.py
   ```
3. 提交并推送：
   ```bash
   git add .
   git commit -m "更新博客内容"
   git push origin main
   ```
4. 访问 `https://vorlunez.github.io` 查看效果

### GitHub Pages 设置确认

在仓库的 **Settings → Pages** 中：
- **Source**：Deploy from a branch
- **Branch**：`main` / `root (/)`
- 点击 Save

> 对于 `username.github.io` 类型的仓库，GitHub 只允许使用 `main` 分支的根目录作为 Pages 源。

---

## 内容规范

### 文章文件名

建议格式：

```
YYYY-MM-DD-文章标题.md
```

例如：`2024-01-15-欢迎来到我的博客.md`

- 文件名前 10 个字符（`YYYY-MM-DD`）会被自动识别为发布日期
- 不含日期前缀时，将使用文件创建时间作为日期

### Markdown 文件格式

支持在文件顶部添加 YAML frontmatter：

```markdown
---
title: 文章标题
date: 2024-01-15
tags: python, flask, 随笔
---

正文内容，支持标准 Markdown 语法。
```

- `title`：文章标题（缺失时使用文件名作为标题）
- `date`：发布日期（缺失时尝试从文件名提取，否则使用文件创建时间）
- `tags`：标签，用英文逗号 `,` 分隔

### 支持的 Markdown 扩展

- fenced_code（代码块）
- tables（表格）
- codehilite（语法高亮，CSS class 为 `highlight`）
- toc（自动生成目录，支持 h2-h3 级标题，带锚点链接）

---

## 代码风格与开发约定

- **双模式支持**：修改模板时，确保同时兼容 Flask (`app.py`) 和静态生成器 (`build.py`)
- **模板变量**：`base.html` 使用 `{{ year }}` 替代 `now().year`，由 `app.py` 和 `build.py` 共同传入
- **静态路径**：模板中 CSS 使用 `/static/style.css`，文章链接使用 `/post/<slug>/`
- **编码**：文件统一使用 UTF-8
- **中文优先**：项目面向中文用户，注释、UI 文本、frontmatter 均使用中文

---

## 测试

本项目**目前没有测试套件**。如需添加测试，建议使用 `pytest` + `Flask test client` 对路由和文章解析逻辑进行覆盖。

---

## 安全注意事项

1. **路径遍历**：`get_post(slug)` 直接拼接文件路径，当前代码未对 `slug` 做严格校验。若部署到公网，建议对 `slug` 进行正则过滤（仅允许 `[a-zA-Z0-9\-_]`）。
2. **XSS 风险**：Markdown 正文通过 `|safe` 直接输出到模板，虽然 Markdown 扩展本身会进行 HTML 转义，但作者可自行插入 HTML。建议仅在信任内容来源的环境中使用。
3. **文件读取**：`get_posts()` 遍历 `posts/` 目录时直接读取所有 `.md` 文件，确保该目录下无敏感文件。
4. **生产部署**：当前使用 Flask 内置开发服务器，生产环境请替换为 gunicorn / uWSGI 等正式 WSGI 服务器，并配合 Nginx 反向代理。
