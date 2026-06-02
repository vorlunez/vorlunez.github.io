#!/usr/bin/env python3
"""
静态站点生成器：将 Markdown 文章渲染为纯静态 HTML，适配 GitHub Pages。

用法:
    python3 build.py

生成的文件直接放在仓库根目录：
    - index.html          首页
    - about/index.html    关于页面
    - post/<slug>/index.html  文章详情页
    - .nojekyll           禁用 Jekyll 处理
"""

import os
import re
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension

POSTS_DIR = os.path.join(os.path.dirname(__file__), 'posts')
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
ROOT_DIR = os.path.dirname(__file__)

# Jinja2 环境（不依赖 Flask）
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def parse_frontmatter(content):
    """解析 Markdown 文件中的 YAML frontmatter"""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        body = match.group(2)
        metadata = {}
        for line in fm_text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"').strip("'")
        return metadata, body
    return {}, content


def get_posts():
    """获取所有文章列表"""
    posts = []
    if not os.path.exists(POSTS_DIR):
        return posts

    for filename in sorted(os.listdir(POSTS_DIR), reverse=True):
        if filename.endswith('.md'):
            filepath = os.path.join(POSTS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            metadata, body = parse_frontmatter(content)
            slug = filename[:-3]

            # 提取摘要（前200个字符）
            summary = re.sub(r'[#*`_\[\]\(\)!]', '', body).replace('\n', ' ')[:200] + '...'

            # 从文件名或 frontmatter 中获取日期
            date_str = metadata.get('date', '')
            if not date_str and filename[:10].replace('-', '').isdigit():
                date_str = filename[:10]
            if not date_str:
                date_str = datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d')

            posts.append({
                'title': metadata.get('title', slug),
                'date': date_str,
                'slug': slug,
                'summary': summary,
                'tags': metadata.get('tags', '').split(',') if metadata.get('tags') else []
            })

    return sorted(posts, key=lambda x: x['date'], reverse=True)


def get_post(slug):
    """获取单篇文章内容"""
    filepath = os.path.join(POSTS_DIR, f'{slug}.md')
    if not os.path.exists(filepath):
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    metadata, body = parse_frontmatter(content)

    md = markdown.Markdown(extensions=[
        'fenced_code',
        'tables',
        CodeHiliteExtension(linenums=False, css_class='highlight'),
        TocExtension(permalink=True, toc_depth='2-3')
    ])
    html_content = md.convert(body)
    toc = md.toc if hasattr(md, 'toc') else ''

    date_str = metadata.get('date', '')
    if not date_str and slug[:10].replace('-', '').isdigit():
        date_str = slug[:10]
    if not date_str:
        date_str = datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d')

    return {
        'title': metadata.get('title', slug),
        'date': date_str,
        'content': html_content,
        'toc': toc,
        'tags': metadata.get('tags', '').split(',') if metadata.get('tags') else []
    }


def write_file(path, content):
    """写入文件，自动创建父目录"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  ✓ {path}')


def build():
    year = datetime.now().year
    posts = get_posts()

    print('🚀 开始生成静态站点...\n')

    # 1. 首页
    print('生成首页...')
    template = env.get_template('index.html')
    html = template.render(posts=posts, year=year)
    write_file(os.path.join(ROOT_DIR, 'index.html'), html)

    # 2. 关于页面
    print('生成关于页面...')
    template = env.get_template('about.html')
    html = template.render(year=year)
    write_file(os.path.join(ROOT_DIR, 'about', 'index.html'), html)

    # 3. 文章详情页
    print(f'生成 {len(posts)} 篇文章...')
    for post_meta in posts:
        slug = post_meta['slug']
        post_data = get_post(slug)
        if not post_data:
            continue
        template = env.get_template('post.html')
        html = template.render(post=post_data, year=year)
        write_file(os.path.join(ROOT_DIR, 'post', slug, 'index.html'), html)

    # 4. 创建 .nojekyll（禁用 Jekyll 处理，避免 _ 开头文件被忽略）
    nojekyll_path = os.path.join(ROOT_DIR, '.nojekyll')
    if not os.path.exists(nojekyll_path):
        with open(nojekyll_path, 'w') as f:
            pass
        print(f'  ✓ {nojekyll_path}')

    # 5. 确保 static/style.css 存在
    css_src = os.path.join(ROOT_DIR, 'static', 'style.css')
    if os.path.exists(css_src):
        print(f'  ✓ {css_src}')
    else:
        print(f'  ✗ 警告：{css_src} 不存在！')

    print('\n✅ 静态站点生成完成！')
    print('请把当前目录下的文件 push 到 GitHub 仓库的 main 分支即可。')


if __name__ == '__main__':
    build()
