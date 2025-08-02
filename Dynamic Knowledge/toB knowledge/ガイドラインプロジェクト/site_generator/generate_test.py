#!/usr/bin/env python3
"""
テスト用サイト生成スクリプト
既存のgenerate_auto.pyを基に、テスト出力用に調整
"""

import os
import sys
import shutil
from pathlib import Path
import re
import markdown
from datetime import datetime
import frontmatter

# プロジェクトのルートディレクトリを設定
PROJECT_ROOT = Path(__file__).parent.parent
CONTENT_DIR = PROJECT_ROOT / "01_現行ガイドライン" / "サイトコンテンツ"
TEMPLATE_DIR = Path(__file__).parent / "_templates"
OUTPUT_DIR = PROJECT_ROOT / "test_output"  # テスト用出力ディレクトリ

# テンプレートファイル
TEMPLATE_FILE = TEMPLATE_DIR / "page_light.html"

# 除外するフォルダ名のパターン
EXCLUDE_FOLDERS = {
    'アーカイブ', 'archive', 'Archive', '_archive',
    'テンプレート', 'template', '_template',
    '下書き', 'draft', '_draft'
}

def create_slug(text):
    """日本語を含むテキストから英語のスラッグを生成"""
    slug_map = {
        '基本情報': 'basic-info',
        'その他': 'others',
        'はじめに': 'introduction',
        'ディレクターの心得': 'director-mindset',
        '業務プロセス': 'work-process',
        'コミュニケーション': 'communication',
        'トラブルシューティング': 'troubleshooting',
        '改善提案': 'feedback',
        '商談マニュアル': 'sales-manual',
        'よくある質問': 'faq',
        '実践': 'practice',
        '事例': 'cases'
    }
    
    # マッピングに存在する場合はそれを使用
    for jp, en in slug_map.items():
        if jp in text:
            return en
    
    # 番号プレフィックスを除去
    text = re.sub(r'^\d+_', '', text)
    
    # 日本語が含まれている場合は簡易的な変換
    if re.search(r'[ぁ-んァ-ヶー一-龠]', text):
        # ファイル名から意味を推測して英語化
        text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
        text = text.strip() or 'page'
    
    # スラッグ化
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def is_excluded_folder(folder_path):
    """フォルダが除外対象かどうかをチェック"""
    folder_name = folder_path.name.lower()
    return any(exclude.lower() in folder_name for exclude in EXCLUDE_FOLDERS)

def get_category_info(file_path, base_dir):
    """ファイルパスからカテゴリ情報を取得"""
    relative_path = file_path.relative_to(base_dir)
    parts = list(relative_path.parts[:-1])  # ファイル名を除く
    
    if parts:
        category = parts[0]
        # カテゴリ番号を除去
        category_clean = re.sub(r'^\d+_', '', category)
        return category_clean
    return "その他"

def extract_order_from_filename(filename):
    """ファイル名から順序番号を抽出"""
    match = re.match(r'^(\d+)[_\s]', filename)
    if match:
        return int(match.group(1))
    return 999  # デフォルト値

def collect_markdown_files(content_dir):
    """Markdownファイルを収集し、カテゴリごとに整理"""
    files_by_category = {}
    
    for md_file in content_dir.rglob("*.md"):
        # 除外フォルダ内のファイルはスキップ
        skip = False
        for parent in md_file.parents:
            if parent == content_dir:
                break
            if is_excluded_folder(parent):
                skip = True
                break
        
        if skip:
            continue
        
        # フロントマターを読み込む
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
        except Exception as e:
            print(f"Warning: Failed to read {md_file}: {e}")
            continue
        
        # カテゴリとタイトルの決定
        category = post.metadata.get('category') or get_category_info(md_file, content_dir)
        title = post.metadata.get('title') or md_file.stem
        order = post.metadata.get('order') or extract_order_from_filename(md_file.name)
        
        # カテゴリごとにファイル情報を保存
        if category not in files_by_category:
            files_by_category[category] = []
        
        files_by_category[category].append({
            'path': md_file,
            'title': title,
            'order': order,
            'content': post.content,
            'metadata': post.metadata
        })
    
    # 各カテゴリ内でソート
    for category in files_by_category:
        files_by_category[category].sort(key=lambda x: (x['order'], x['title']))
    
    return files_by_category

def generate_html(md_content, title, template_content, nav_html, category):
    """MarkdownコンテンツからHTMLを生成"""
    # Markdown to HTML変換
    extensions = ['extra', 'codehilite', 'toc', 'tables', 'fenced_code']
    md = markdown.Markdown(extensions=extensions)
    content_html = md.convert(md_content)
    
    # ビデオのレスポンシブ対応
    content_html = re.sub(
        r'width="\d+" height="\d+"',
        'width="800" height="450" style="max-width: 100%; height: auto;"',
        content_html
    )
    
    # テンプレートに値を埋め込む
    html = template_content
    html = html.replace('{{title}}', title)
    html = html.replace('{{content}}', content_html)
    html = html.replace('{{navigation}}', nav_html)
    html = html.replace('{{category}}', category)
    html = html.replace('{{generated_date}}', datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    return html

def generate_navigation(files_by_category, current_file=None):
    """ナビゲーションHTMLを生成"""
    nav_items = []
    
    # カテゴリをソート（番号プレフィックスがある場合は考慮）
    sorted_categories = sorted(files_by_category.keys(), 
                             key=lambda x: (extract_order_from_filename(x), x))
    
    for category in sorted_categories:
        nav_items.append(f'<div class="nav-category">{category}</div>')
        
        for file_info in files_by_category[category]:
            slug = create_slug(file_info['title'])
            filename = f"{slug}.html"
            
            # アクティブなリンクをハイライト
            active_class = ""
            if current_file and file_info['path'] == current_file:
                active_class = ' class="active"'
            
            nav_items.append(
                f'<a href="{filename}"{active_class}>{file_info["title"]}</a>'
            )
    
    # ホームリンクとテスト機能へのリンクを追加
    nav_html = '<a href="index.html">ホーム</a>\n'
    nav_html += '<div class="nav-divider"></div>\n'
    nav_html += '\n'.join(nav_items)
    nav_html += '\n<div class="nav-divider"></div>\n'
    nav_html += '<a href="../99_テスト機能/feedback_system/form_template/feedback_page.html" style="background-color: #ff6b6b; color: white;">📝 改善提案</a>'
    
    return nav_html

def copy_static_files():
    """静的ファイルをコピー"""
    static_files = ['style.css', 'script.js']
    template_static_dir = TEMPLATE_DIR / "static"
    
    if template_static_dir.exists():
        for static_file in static_files:
            src = template_static_dir / static_file
            if src.exists():
                dst = OUTPUT_DIR / static_file
                shutil.copy2(src, dst)
                print(f"Copied {static_file}")

def main():
    """メイン処理"""
    print("=== テスト用サイト生成開始 ===")
    print(f"コンテンツディレクトリ: {CONTENT_DIR}")
    print(f"出力ディレクトリ: {OUTPUT_DIR}")
    
    # 出力ディレクトリを作成（既存の場合は削除）
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    print(f"Created output directory: {OUTPUT_DIR}")
    
    # テンプレートを読み込む
    if not TEMPLATE_FILE.exists():
        print(f"Error: Template file not found: {TEMPLATE_FILE}")
        return
    
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Markdownファイルを収集
    files_by_category = collect_markdown_files(CONTENT_DIR)
    
    if not files_by_category:
        print("Warning: No markdown files found!")
        return
    
    print(f"\nFound {sum(len(files) for files in files_by_category.values())} markdown files")
    
    # 生成されたファイルのマッピング
    generated_files = {}
    
    # 各ファイルに対してHTMLを生成
    for category, files in files_by_category.items():
        print(f"\nProcessing category: {category}")
        
        for file_info in files:
            md_file = file_info['path']
            title = file_info['title']
            
            # ファイル名の重複を解決
            base_slug = create_slug(title)
            slug = base_slug
            counter = 1
            
            while slug in generated_files:
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            filename = f"{slug}.html"
            generated_files[slug] = filename
            
            # ナビゲーションを生成
            nav_html = generate_navigation(files_by_category, md_file)
            
            # HTMLを生成
            html_content = generate_html(
                file_info['content'], 
                title, 
                template_content, 
                nav_html,
                category
            )
            
            # ファイルを保存
            output_path = OUTPUT_DIR / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"  Generated: {filename} <- {md_file.name}")
    
    # インデックスページの生成
    index_content = generate_index_page(files_by_category, template_content)
    with open(OUTPUT_DIR / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_content)
    print("\nGenerated: index.html")
    
    # 静的ファイルをコピー
    copy_static_files()
    
    # .nojekyllファイルを作成（GitHub Pages用）
    (OUTPUT_DIR / '.nojekyll').touch()
    
    print(f"\n=== テスト用サイト生成完了 ===")
    print(f"生成されたファイル数: {len(generated_files) + 1}")
    print(f"出力先: {OUTPUT_DIR}")
    print("\n⚠️  これはテスト版です。本番環境には影響しません。")

def generate_index_page(files_by_category, template_content):
    """インデックスページを生成"""
    content = """
# Harukazeガイドライン（テスト版）

このサイトはHarukazeのディレクター向けガイドラインのテスト版です。

## 🆕 新機能テスト中

- **改善提案システム**: ガイドラインへのフィードバックを簡単に送信できます
- **AIアシスタント**: （準備中）ガイドラインに関する質問に即座に回答

## 📚 コンテンツ一覧
"""
    
    # カテゴリごとにリンクを生成
    for category in sorted(files_by_category.keys(), 
                         key=lambda x: (extract_order_from_filename(x), x)):
        content += f"\n### {category}\n\n"
        
        for file_info in files_by_category[category]:
            slug = create_slug(file_info['title'])
            filename = f"{slug}.html"
            content += f"- [{file_info['title']}]({filename})\n"
    
    content += """
## 📝 フィードバック

ガイドラインをより良くするため、ぜひご意見をお聞かせください。

→ [改善提案フォームはこちら](../99_テスト機能/feedback_system/form_template/feedback_page.html)
"""
    
    # ナビゲーションを生成
    nav_html = generate_navigation(files_by_category)
    
    # HTMLを生成
    return generate_html(content, "Harukazeガイドライン - テスト版", 
                        template_content, nav_html, "ホーム")

if __name__ == "__main__":
    main()