#!/usr/bin/env python3
"""
ガイドライン静的サイト生成ツール（site_config.json対応版）
"""

import os
import json
import shutil
import markdown
from pathlib import Path
import re

# 設定ファイルを読み込む
with open('site_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 設定
ROOT_FOLDER = os.getcwd()
SOURCE_FOLDER = config['source_folder']
OUTPUT_FOLDER = config['output_folder']
TEMPLATE_FILE = config['template_file']

def generate_site():
    """サイトを生成"""
    print("🚀 ガイドライン静的サイト生成を開始します...")
    
    # 出力フォルダをクリーンアップ
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)
    
    # テンプレートを読み込む
    template_path = os.path.join(ROOT_FOLDER, TEMPLATE_FILE)
    if not os.path.exists(template_path):
        print(f"❌ テンプレートファイルが見つかりません: {TEMPLATE_FILE}")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 各ファイルを処理
    nav_items = []
    
    for filename in config['include_files']:
        file_path = os.path.join(ROOT_FOLDER, SOURCE_FOLDER, filename)
        
        if not os.path.exists(file_path):
            print(f"⚠️  ファイルが見つかりません: {file_path}")
            continue
        
        # マークダウンを読み込んで変換
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # マークダウンをHTMLに変換
        html_content = markdown.markdown(content, extensions=['fenced_code', 'tables', 'toc'])
        
        # ファイル情報を取得
        file_info = config['files'].get(filename, {})
        title = file_info.get('title', Path(filename).stem)
        category = file_info.get('category', '未分類')
        
        # 出力ファイル名を決定
        safe_name = config['filename_replacements'].get(Path(filename).stem, Path(filename).stem)
        output_filename = f"{safe_name}.html"
        
        # HTMLを生成
        page_html = template
        page_html = page_html.replace('{{title}}', title)
        page_html = page_html.replace('{{content}}', html_content)
        page_html = page_html.replace('{{nav_items}}', '')  # 後で更新
        
        # ファイルを保存
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(page_html)
        
        print(f"✅ 生成完了: {output_filename}")
        
        # ナビゲーション項目を追加
        nav_items.append({
            'title': title,
            'url': output_filename,
            'category': category
        })
    
    # 全ページのナビゲーションを更新
    nav_html = generate_navigation(nav_items)
    
    for filename in os.listdir(OUTPUT_FOLDER):
        if filename.endswith('.html'):
            file_path = os.path.join(OUTPUT_FOLDER, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content = content.replace('{{nav_items}}', nav_html)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    print(f"\n✅ サイト生成が完了しました！")
    print(f"📁 出力先: {os.path.join(ROOT_FOLDER, OUTPUT_FOLDER)}")

def generate_navigation(nav_items):
    """ナビゲーションHTMLを生成"""
    nav_html = []
    
    # カテゴリごとにグループ化
    categories = {}
    for item in nav_items:
        category = item['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    # HTMLを生成
    for category, items in categories.items():
        nav_html.append(f'<div class="category">{category}</div>')
        for item in items:
            nav_html.append(f'<a href="{item["url"]}">{item["title"]}</a>')
    
    return '\n'.join(nav_html)

if __name__ == "__main__":
    generate_site()