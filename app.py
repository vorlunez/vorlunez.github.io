import os
import re
from datetime import datetime
from flask import Flask, render_template, abort
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension

app = Flask(__name__)

POSTS_DIR = os.path.join(os.path.dirname(__file__), 'posts')


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


@app.route('/')
def index():
    posts = get_posts()
    return render_template('index.html', posts=posts)


@app.route('/post/<slug>')
def post(slug):
    post_data = get_post(slug)
    if not post_data:
        abort(404)
    return render_template('post.html', post=post_data)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
