# AGENTS.md

本文件面向 AI 编码助手，用于快速了解本项目的技术栈、架构与开发规范。

---

## 项目概述

本项目是一个**极简的个人博客**，使用 Python + Flask 构建。博客没有数据库，所有文章内容直接读取 `posts/` 目录下的 Markdown 文件并动态渲染为 HTML。

核心特点：
- 纯静态文件驱动：将 `.md` 文件放入 `posts/` 目录即可发布文章
- 支持 YAML frontmatter 设置标题、日期、标签
- 支持 Markdown 语法、代码高亮、自动生成目录（TOC）
- 单文件应用，无外部数据库依赖

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask 3.0.3 |
| Markdown 渲染 | Python-Markdown 3.6（含 fenced_code、tables、codehilite、toc 扩展）|
| 代码高亮 | Pygments 2.18.0 |
| 模板引擎 | Jinja2（Flask 内置）|
| 前端样式 | 原生 CSS（无 JS 框架）|
| 字体 | Google Fonts: Noto Serif SC / Noto Sans SC |

---

## 项目结构

```
.
├── app.py              # 唯一的 Flask 应用入口，包含路由、文章解析逻辑
├── requirements.txt    # Python 依赖
├── start.sh            # 一键启动脚本（安装依赖 + 运行服务）
├── posts/              # 文章目录，存放 Markdown 文件
│   └── YYYY-MM-DD-标题.md
├── templates/          # Jinja2 模板
│   ├── base.html       # 基础布局（头部导航、页脚、CSS 引用）
│   ├── index.html      # 首页：文章列表
│   ├── post.html       # 文章详情页（含 TOC、正文、返回链接）
│   └── about.html      # 关于页面
└── static/
    └── style.css       # 完整样式表（响应式、Markdown 渲染样式、代码高亮）
```

---

## 运行方式

### 一键启动（推荐）

```bash
./start.sh
```

脚本会：
1. 自动安装 `requirements.txt` 中的依赖（`pip3 install -r requirements.txt`）
2. 启动 Flask 内置服务器于 `http://localhost:5000`

### 手动启动

```bash
pip install -r requirements.txt
python app.py
```

生产环境请注意：`app.py` 中 `debug=False`，但内置服务器不适合高并发生产部署，建议使用 gunicorn 等 WSGI 服务器。

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

-  fenced_code（代码块）
-  tables（表格）
-  codehilite（语法高亮，CSS class 为 `highlight`）
-  toc（自动生成目录，支持 h2-h3 级标题，带锚点链接）

---

## 代码风格与开发约定

- **单文件应用**：所有后端逻辑集中在 `app.py`，新增功能时请保持简洁
- **编码**：文件统一使用 UTF-8
- **模板继承**：所有页面继承 `base.html`，通过 `{% block content %}` 填充主体
- **静态资源**：CSS 与图片放在 `static/`，模板中使用 `url_for('static', filename='...')` 引用
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
