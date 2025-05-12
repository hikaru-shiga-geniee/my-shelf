#!/usr/bin/env python3
import argparse
import csv
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

from extract_text import extract_text

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# 定数
SHELF_DIR = Path("shelf")


def setup_shelf():
    """
    シェルフディレクトリが存在しない場合は作成します。
    """
    if not SHELF_DIR.exists():
        SHELF_DIR.mkdir(exist_ok=True)
        logger.info(f"シェルフディレクトリを作成しました: {SHELF_DIR}")


def add_book(args):
    """
    新しい本を追加します。
    """
    book_path = Path(args.file)
    if not book_path.exists():
        logger.error(f"ファイルが見つかりません: {book_path}")
        return

    book_id = args.id
    title = args.title
    memo = args.memo or ""

    # 本のディレクトリを作成
    book_dir = SHELF_DIR / book_id
    if book_dir.exists():
        logger.error(f"ID '{book_id}' は既に使用されています。")
        return
    book_dir.mkdir(exist_ok=True)

    # 本のファイルをコピー
    dest_file = book_dir / book_path.name
    shutil.copy2(book_path, dest_file)

    # テキストを抽出して保存
    text = extract_text(book_path)
    if text:
        text_file = book_dir / f"{book_id}.txt"
        text_file.write_text(text)
    
    # メタデータをJSONで保存
    now = datetime.now().isoformat()
    metadata = {
        "id": book_id,
        "title": title,
        "memo": memo,
        "created_at": now,
        "updated_at": now
    }
    json_file = book_dir / f"{book_id}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    logger.info(f"本 '{book_id}' を追加しました。")


def show_book(args):
    """
    本の内容を表示します。
    """
    book_id = args.id
    book_dir = SHELF_DIR / book_id
    
    if not book_dir.exists():
        logger.error(f"ID '{book_id}' の本が見つかりません。")
        return
    
    text_file = book_dir / f"{book_id}.txt"
    if not text_file.exists():
        logger.error(f"テキストファイルが見つかりません: {text_file}")
        return
    
    print(text_file.read_text())


def edit_book(args):
    """
    本のメタデータを編集します。
    """
    book_id = args.id
    book_dir = SHELF_DIR / book_id
    
    if not book_dir.exists():
        logger.error(f"ID '{book_id}' の本が見つかりません。")
        return
    
    json_file = book_dir / f"{book_id}.json"
    if not json_file.exists():
        logger.error(f"メタデータファイルが見つかりません: {json_file}")
        return
    
    # 現在のメタデータを読み込む
    with open(json_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    # 更新するフィールドを処理
    if args.title:
        metadata["title"] = args.title
    
    if args.memo:
        metadata["memo"] = args.memo
    
    metadata["updated_at"] = datetime.now().isoformat()
    
    # 更新したメタデータを保存
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    
    logger.info(f"本 '{book_id}' のメタデータを更新しました。")


def delete_book(args):
    """
    本を削除します。
    """
    book_id = args.id
    book_dir = SHELF_DIR / book_id
    
    if not book_dir.exists():
        logger.error(f"ID '{book_id}' の本が見つかりません。")
        return
    
    shutil.rmtree(book_dir)
    logger.info(f"本 '{book_id}' を削除しました。")


def list_books(args):
    """
    すべての本をリスト表示します。
    """
    if not SHELF_DIR.exists() or not any(SHELF_DIR.iterdir()):
        logger.info("本棚は空です。")
        return
    
    books = []
    for book_dir in SHELF_DIR.iterdir():
        if not book_dir.is_dir():
            continue
        
        json_file = book_dir / f"{book_dir.name}.json"
        if not json_file.exists():
            continue
        
        with open(json_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            books.append(metadata)
    
    # CSVとして出力
    writer = csv.DictWriter(sys.stdout, fieldnames=["id", "title", "memo", "created_at", "updated_at"])
    writer.writeheader()
    writer.writerows(books)


def main():
    """
    メイン関数です。コマンドライン引数を解析し、適切な処理を実行します。
    """
    parser = argparse.ArgumentParser(description="本棚管理システム")
    subparsers = parser.add_subparsers(dest="command", help="コマンド")
    
    # add コマンド
    add_parser = subparsers.add_parser("add", help="本を追加")
    add_parser.add_argument("file", help="追加する本のファイルパス")
    add_parser.add_argument("id", help="本のID")
    add_parser.add_argument("title", help="本のタイトル")
    add_parser.add_argument("--memo", help="本に関するメモ")
    
    # show コマンド
    show_parser = subparsers.add_parser("show", help="本の内容を表示")
    show_parser.add_argument("id", help="表示する本のID")
    
    # edit コマンド
    edit_parser = subparsers.add_parser("edit", help="本のメタデータを編集")
    edit_parser.add_argument("id", help="編集する本のID")
    edit_parser.add_argument("--title", help="新しいタイトル")
    edit_parser.add_argument("--memo", help="新しいメモ")
    
    # delete コマンド
    delete_parser = subparsers.add_parser("delete", help="本を削除")
    delete_parser.add_argument("id", help="削除する本のID")
    
    # list コマンド
    list_parser = subparsers.add_parser("list", help="すべての本をリスト表示")
    
    args = parser.parse_args()
    
    # シェルフディレクトリを準備
    setup_shelf()
    
    # コマンドに応じた処理を実行
    if args.command == "add":
        add_book(args)
    elif args.command == "show":
        show_book(args)
    elif args.command == "edit":
        edit_book(args)
    elif args.command == "delete":
        delete_book(args)
    elif args.command == "list":
        list_books(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
