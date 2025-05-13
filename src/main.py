#!/usr/bin/env python3
import argparse
import csv
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from extract_text import extract_text

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# 定数
SHELF_DIR = Path("shelf_data")


def setup_shelf() -> None:
    """
    シェルフディレクトリが存在しない場合は作成します。
    
    Returns:
        None
    """
    if not SHELF_DIR.exists():
        SHELF_DIR.mkdir(exist_ok=True)
        logger.info(f"シェルフディレクトリを作成しました: {SHELF_DIR}")


def handle_add(file_path: str, book_id: str, title: str, memo: str = "") -> None:
    """
    新しい本を追加します。
    
    指定されたファイルパスから本をシステムに追加し、メタデータを保存します。
    テキストを抽出して保存し、元のファイルもコピーします。
    
    Args:
        file_path (str): 追加する本のファイルパス
        book_id (str): 本のID（一意である必要があります）
        title (str): 本のタイトル
        memo (str, optional): 本に関するメモ。デフォルトは空文字列。
        
    Returns:
        None
    """
    book_path = Path(file_path)
    if not book_path.exists():
        logger.error(f"ファイルが見つかりません: {book_path}")
        sys.exit(1)

    # 本のディレクトリを作成
    book_dir = SHELF_DIR / book_id
    if book_dir.exists():
        logger.error(f"ID '{book_id}' は既に使用されています。")
        sys.exit(1)
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
    metadata: Dict[str, str] = {
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


def handle_show(book_id: str) -> None:
    """
    本の内容を表示します。
    
    指定されたIDの本のテキスト内容を標準出力に表示します。
    
    Args:
        book_id (str): 表示する本のID
        
    Returns:
        None
    """
    book_dir = SHELF_DIR / book_id
    
    if not book_dir.exists():
        logger.error(f"ID '{book_id}' の本が見つかりません。")
        sys.exit(1)
    
    text_file = book_dir / f"{book_id}.txt"
    if not text_file.exists():
        logger.error(f"テキストファイルが見つかりません: {text_file}")
        sys.exit(1)
    
    print(text_file.read_text())


def handle_edit(book_id: str, title: Optional[str] = None, memo: Optional[str] = None) -> None:
    """
    本のメタデータを編集します。
    
    指定されたIDの本のメタデータを更新します。タイトルやメモを変更できます。
    
    Args:
        book_id (str): 編集する本のID
        title (Optional[str], optional): 新しいタイトル。指定しない場合は変更しません。
        memo (Optional[str], optional): 新しいメモ。指定しない場合は変更しません。
        
    Returns:
        None
    """
    book_dir = SHELF_DIR / book_id
    
    if not book_dir.exists():
        logger.error(f"ID '{book_id}' の本が見つかりません。")
        sys.exit(1)
    
    json_file = book_dir / f"{book_id}.json"
    if not json_file.exists():
        logger.error(f"メタデータファイルが見つかりません: {json_file}")
        sys.exit(1)
    
    # 現在のメタデータを読み込む
    with open(json_file, "r", encoding="utf-8") as f:
        metadata: Dict[str, str] = json.load(f)
    
    # 更新するフィールドを処理
    if title:
        metadata["title"] = title
    
    if memo:
        metadata["memo"] = memo
    
    metadata["updated_at"] = datetime.now().isoformat()
    
    # 更新したメタデータを保存
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    
    logger.info(f"本 '{book_id}' のメタデータを更新しました。")


def handle_delete(book_id: str) -> None:
    """
    本を削除します。
    
    指定されたIDの本をシステムから完全に削除します。
    本のファイル、テキスト、メタデータなど、すべてのデータが削除されます。
    
    Args:
        book_id (str): 削除する本のID
        
    Returns:
        None
    """
    book_dir = SHELF_DIR / book_id
    
    if not book_dir.exists():
        logger.error(f"ID '{book_id}' の本が見つかりません。")
        sys.exit(1)
    
    shutil.rmtree(book_dir)
    logger.info(f"本 '{book_id}' を削除しました。")


def handle_list() -> None:
    """
    すべての本をリスト表示します。
    
    システムに登録されているすべての本のメタデータをCSV形式で標準出力に表示します。
    本が登録されていない場合はその旨をログに記録します。
    
    Returns:
        None
    """
    if not SHELF_DIR.exists() or not any(SHELF_DIR.iterdir()):
        logger.info("本棚は空です。")
        return
    
    books: List[Dict[str, str]] = []
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


def handle_info(book_id: str) -> None:
    """
    本のメタデータ情報を表示します。
    
    指定されたIDの本のメタデータをフォーマットしてJSON形式で標準出力に表示します。
    
    Args:
        book_id (str): 情報を表示する本のID
        
    Returns:
        None
    """
    book_dir = SHELF_DIR / book_id
    
    if not book_dir.exists():
        logger.error(f"ID '{book_id}' の本が見つかりません。")
        sys.exit(1)
    
    json_file = book_dir / f"{book_id}.json"
    if not json_file.exists():
        logger.error(f"メタデータファイルが見つかりません: {json_file}")
        sys.exit(1)
    
    # メタデータを読み込む
    with open(json_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    # 整形されたJSONを標準出力に表示
    print(json.dumps(metadata, ensure_ascii=False, indent=4))


def setup_subparsers(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    コマンドライン引数のサブパーサーを設定します。
    
    各コマンド（add, show, edit, delete, list, info）に対応するサブパーサーを作成し、
    それぞれに必要な引数を設定します。
    
    Args:
        parser (argparse.ArgumentParser): 引数パーサーのインスタンス
        
    Returns:
        argparse.ArgumentParser: サブパーサーが設定されたパーサー
    """
    subparsers = parser.add_subparsers(dest="command", help="コマンド")
    
    # add コマンド
    add_parser = subparsers.add_parser("add", help="本を追加")
    add_parser.add_argument("file", help="追加する本のファイルパス")
    add_parser.add_argument("id", help="本のID")
    add_parser.add_argument("title", help="本のタイトル")
    add_parser.add_argument("--memo", help="本に関するメモ")
    add_parser.set_defaults(func="add")
    
    # show コマンド
    show_parser = subparsers.add_parser("show", help="本の内容を表示")
    show_parser.add_argument("id", help="表示する本のID")
    show_parser.set_defaults(func="show")
    
    # edit コマンド
    edit_parser = subparsers.add_parser("edit", help="本のメタデータを編集")
    edit_parser.add_argument("id", help="編集する本のID")
    edit_parser.add_argument("--title", help="新しいタイトル")
    edit_parser.add_argument("--memo", help="新しいメモ")
    edit_parser.set_defaults(func="edit")
    
    # delete コマンド
    delete_parser = subparsers.add_parser("delete", help="本を削除")
    delete_parser.add_argument("id", help="削除する本のID")
    delete_parser.set_defaults(func="delete")
    
    # list コマンド
    list_parser = subparsers.add_parser("list", help="すべての本をリスト表示")
    list_parser.set_defaults(func="list")
    
    # info コマンド
    info_parser = subparsers.add_parser("info", help="本のメタデータ情報を表示")
    info_parser.add_argument("id", help="情報を表示する本のID")
    info_parser.set_defaults(func="info")
    
    return parser


def main() -> None:
    """
    メイン関数です。コマンドライン引数を解析し、適切な処理を実行します。
    
    コマンドライン引数を解析し、指定されたコマンドに応じて対応するハンドラー関数を
    呼び出します。シェルフディレクトリが存在しない場合は作成します。
    
    Returns:
        None
    """
    parser = argparse.ArgumentParser(description="本棚管理システム")
    setup_subparsers(parser)
    
    args = parser.parse_args()
    
    # シェルフディレクトリを準備
    setup_shelf()
    
    # コマンドに応じた処理を実行
    if hasattr(args, 'func'):
        if args.func == "add":
            handle_add(args.file, args.id, args.title, args.memo or "")
        elif args.func == "show":
            handle_show(args.id)
        elif args.func == "edit":
            handle_edit(args.id, args.title, args.memo)
        elif args.func == "delete":
            handle_delete(args.id)
        elif args.func == "list":
            handle_list()
        elif args.func == "info":
            handle_info(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
