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
TEMPLATE_FILE = TEMPLATE_DIR / "page_light_with_ai.html"

# 除外するフォルダ名のパターン
EXCLUDE_FOLDERS = {
    'アーカイブ', 'archive', 'Archive', '_archive',
    'テンプレート', 'template', '_template',
    '下書き', 'draft', '_draft'
}

def create_slug(text):
    """日本語を含むテキストから英語のスラッグを生成"""
    # まず番号プレフィックスを除去（タイトル表示用の処理と同じ）
    text = re.sub(r'^\d+[_\-]\s*', '', text)
    
    # 詳細なマッピング
    slug_map = {
        # 基本情報
        'はじめに': 'introduction',
        'ディレクターの心得': 'director-mindset',
        '全体の業務プロセス': 'work-process',
        'コミュニケーションガイド': 'communication',
        '代表的なトラブルシューティング': 'troubleshooting',
        # 商談マニュアル
        '法人商談の全体像': 'sales-overview',
        '法人商談の心得': 'sales-mindset',
        '信頼関係の構築テクニック': 'trust-building',
        'ヒアリングマスター講座': 'hearing-master',
        '提案力を高める実践テクニック': 'proposal-techniques',
        'クロージング成功の秘訣': 'closing-success',
        '商材別の攻略法': 'product-strategies',
        '難易度別の対処法': 'difficulty-handling',
        # その他
        'AIアシスタント': 'ai-assistant',
        'よくある質問': 'faq',
        'ガイドライン改善提案': 'feedback',
        '実践改善事例集': 'improvement-cases',
        # カテゴリ名
        '基本情報': 'basic-info',
        'その他': 'others',
        '商談マニュアル': 'sales-manual'
    }
    
    # 完全一致でマッピングを確認
    if text in slug_map:
        return slug_map[text]
    
    # 部分一致でマッピングを確認
    for jp, en in slug_map.items():
        if jp in text:
            return en
    
    # 日本語が含まれている場合は簡易的な変換
    if re.search(r'[ぁ-んァ-ヶー一-龠]', text):
        # デフォルトでpage-N形式
        return 'page'
    
    # スラッグ化
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-') or 'page'

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
        # タイトルから番号プレフィックスを削除
        raw_title = post.metadata.get('title') or md_file.stem
        title = re.sub(r'^\d+[_\-]\s*', '', raw_title)  # 01_, 02- などを削除
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
    
    # テンプレートに値を埋め込む（大文字のプレースホルダーに対応）
    html = template_content
    html = html.replace('{{TITLE}}', title)
    html = html.replace('{{CONTENT}}', content_html)
    html = html.replace('{{SIDEBAR}}', nav_html)
    html = html.replace('{{title}}', title)  # 小文字版も念のため
    html = html.replace('{{content}}', content_html)
    html = html.replace('{{navigation}}', nav_html)
    html = html.replace('{{category}}', category)
    html = html.replace('{{generated_date}}', datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    return html

def generate_navigation(files_by_category, current_file=None):
    """ナビゲーションHTMLを生成"""
    nav_items = []
    
    # サイドバーヘッダーを追加
    nav_items.append('<div class="sidebar-header">')
    nav_items.append('    <a href="index.html" style="text-decoration: none;">')
    nav_items.append('        <h1>Harukazeガイドライン</h1>')
    nav_items.append('    </a>')
    nav_items.append('    <p>ディレクター向け品質管理ガイド</p>')
    nav_items.append('</div>')
    nav_items.append('<div class="sidebar-nav">')
    
    # カテゴリの順序を定義（基本情報 → 商談マニュアル → その他）
    category_order = {
        '基本情報': 1,
        '商談マニュアル': 2,
        'その他': 3
    }
    
    # カテゴリをソート
    sorted_categories = sorted(files_by_category.keys(), 
                             key=lambda x: (category_order.get(x, 999), x))
    
    # ホームリンク
    nav_items.append('<a href="index.html" class="nav-item">ホーム</a>')
    nav_items.append('<div class="nav-divider"></div>')
    
    for category in sorted_categories:
        nav_items.append('<div class="category">')
        nav_items.append(f'    <div class="category-title">{category}</div>')
        
        for file_info in files_by_category[category]:
            # ガイドライン改善提案はナビゲーションから除外
            if file_info['title'] == 'ガイドライン改善提案':
                continue
                
            # 既に生成されたファイル名を使用
            filename = file_info.get('filename', f"{create_slug(file_info['title'])}.html")
            
            # アクティブなリンクをハイライト
            active_class = " active" if current_file and file_info['path'] == current_file else ""
            
            nav_items.append(
                f'    <a href="{filename}" class="nav-item{active_class}">{file_info["title"]}</a>'
            )
        
        nav_items.append('</div>')
    
    nav_items.append('</div>')  # sidebar-nav を閉じる
    
    # サイドバーフッターにリンクを追加
    nav_items.append('<div class="sidebar-footer">')
    nav_items.append('    <button class="footer-link" id="aiToggleBtn" onclick="toggleAiPanel()">AIチャット</button>')
    nav_items.append('    <div class="footer-divider"></div>')
    nav_items.append('    <a href="feedback.html" class="footer-link">ガイドライン改善提案</a>')
    nav_items.append('</div>')
    
    return '\n'.join(nav_items)

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
            file_info['filename'] = filename  # ファイル名を保存
            
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
            # 既に生成されたファイル名を使用
            filename = file_info.get('filename', f"{create_slug(file_info['title'])}.html")
            content += f"- [{file_info['title']}]({filename})\n"
    
    content += """
## 📝 フィードバック

ガイドラインをより良くするため、ぜひご意見をお聞かせください。

→ [改善提案フォームはこちら](feedback.html)
"""
    
    # ナビゲーションを生成
    nav_html = generate_navigation(files_by_category)
    
    # HTMLを生成
    return generate_html(content, "Harukazeガイドライン - テスト版", 
                        template_content, nav_html, "ホーム")

if __name__ == "__main__":
    main()