import os
import sys
import json
import shutil
import pytest
from pathlib import Path

# テスト対象のモジュールをインポートできるようにする
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import (
    handle_add,
    handle_show,
    handle_info,
    handle_edit,
    handle_delete,
    handle_list,
    SHELF_DIR,
)


@pytest.fixture
def setup_teardown():
    """テスト前後の環境設定と後片付け"""
    # テスト用のシェルフディレクトリを作成
    if SHELF_DIR.exists():
        shutil.rmtree(SHELF_DIR)
    SHELF_DIR.mkdir(exist_ok=True)

    yield

    # テスト後に掃除
    if SHELF_DIR.exists():
        shutil.rmtree(SHELF_DIR)


# テスト用のパラメータ
test_files = [
    {
        "path": "tests/files/test.pdf",
        "id": "pdf_book",
        "title": "PDFの本",
        "memo": "PDFのメモ",
    },
    {
        "path": "tests/files/test.epub",
        "id": "epub_book",
        "title": "EPUBの本",
        "memo": "EPUBのメモ",
    },
    {
        "path": "tests/files/test.txt",
        "id": "txt_book",
        "title": "テキストの本",
        "memo": "テキストのメモ",
    },
]


@pytest.mark.parametrize("file_info", test_files)
def test_add_book_parametrized(setup_teardown, file_info):
    """パラメータ化した本の追加機能テスト"""
    test_file = Path(file_info["path"])
    book_id = file_info["id"]
    title = file_info["title"]
    memo = file_info["memo"]

    handle_add(str(test_file), book_id, title, memo)

    # ディレクトリとファイルが作成されたことを確認
    book_dir = SHELF_DIR / book_id
    assert book_dir.exists()

    # メタデータファイルが作成されたことを確認
    json_file = book_dir / f"{book_id}.json"
    assert json_file.exists()

    # メタデータの内容を確認
    with open(json_file, encoding="utf-8") as f:
        metadata = json.load(f)

    assert metadata["id"] == book_id
    assert metadata["title"] == title
    assert metadata["memo"] == memo


@pytest.mark.parametrize("file_info", test_files)
def test_show_book_parametrized(setup_teardown, capsys, file_info):
    """パラメータ化した本の表示機能テスト"""
    test_file = Path(file_info["path"])
    book_id = file_info["id"]
    title = file_info["title"]
    memo = file_info["memo"]

    handle_add(str(test_file), book_id, title, memo)

    # 本の内容を表示
    handle_show(book_id)

    # 標準出力をキャプチャして内容を確認
    captured = capsys.readouterr()
    assert captured.out  # 何らかの出力があることを確認


@pytest.mark.parametrize("file_info", test_files)
def test_info_book_parametrized(setup_teardown, capsys, file_info):
    """パラメータ化した本の情報表示機能テスト"""
    test_file = Path(file_info["path"])
    book_id = file_info["id"]
    title = file_info["title"]
    memo = file_info["memo"]

    handle_add(str(test_file), book_id, title, memo)

    # 本の情報を表示
    handle_info(book_id)

    # 標準出力をキャプチャして内容を確認
    captured = capsys.readouterr()
    output = json.loads(captured.out)

    assert output["id"] == book_id
    assert output["title"] == title
    assert output["memo"] == memo


@pytest.mark.parametrize("file_info", test_files)
def test_edit_book_parametrized(setup_teardown, file_info):
    """パラメータ化した本の編集機能テスト"""
    test_file = Path(file_info["path"])
    book_id = file_info["id"]
    title = file_info["title"]
    memo = file_info["memo"]

    handle_add(str(test_file), book_id, title, memo)

    # 本の情報を編集
    new_title = f"新しい{title}"
    new_memo = f"新しい{memo}"
    handle_edit(book_id, new_title, new_memo)

    # 編集後のメタデータを確認
    json_file = SHELF_DIR / book_id / f"{book_id}.json"
    with open(json_file, encoding="utf-8") as f:
        metadata = json.load(f)

    assert metadata["title"] == new_title
    assert metadata["memo"] == new_memo


@pytest.mark.parametrize("file_info", test_files)
def test_delete_book_parametrized(setup_teardown, file_info):
    """パラメータ化した本の削除機能テスト"""
    test_file = Path(file_info["path"])
    book_id = file_info["id"]
    title = file_info["title"]
    memo = file_info["memo"]

    handle_add(str(test_file), book_id, title, memo)

    # 本のディレクトリが存在することを確認
    book_dir = SHELF_DIR / book_id
    assert book_dir.exists()

    # 本を削除
    handle_delete(book_id)

    # 本のディレクトリが削除されたことを確認
    assert not book_dir.exists()


def test_list_books_parametrized(setup_teardown, capsys):
    """パラメータ化した本のリスト表示機能テスト"""
    # 複数の本を追加
    for file_info in test_files:
        handle_add(
            file_info["path"], file_info["id"], file_info["title"], file_info["memo"]
        )

    # 本のリストを表示
    handle_list()

    # 標準出力をキャプチャして内容を確認
    captured = capsys.readouterr()

    # CSVヘッダーと複数の本のエントリがあることを確認
    lines = captured.out.strip().split("\n")
    assert len(lines) == len(test_files) + 1  # ヘッダー + 本の数
    assert "id,title,memo,created_at,updated_at" in lines[0]

    # 各本のIDが出力に含まれていることを確認
    for file_info in test_files:
        assert file_info["id"] in captured.out


@pytest.mark.parametrize("file_info", test_files)
def test_full_workflow_parametrized(setup_teardown, capsys, file_info):
    """パラメータ化した完全なワークフローテスト"""
    test_file = Path(file_info["path"])
    book_id = file_info["id"]
    title = file_info["title"]
    memo = file_info["memo"]

    # 1. 本の追加
    handle_add(str(test_file), book_id, title, memo)

    # 2. 本の内容表示
    handle_show(book_id)
    show_output = capsys.readouterr().out
    assert show_output  # 何らかの出力があることを確認

    # 3. 本の情報表示
    handle_info(book_id)
    info_output = json.loads(capsys.readouterr().out)
    assert info_output["title"] == title

    # 4. 本の情報編集
    new_title = f"新しい{title}"
    new_memo = f"新しい{memo}"
    handle_edit(book_id, new_title, new_memo)

    # 5. 編集後の情報表示
    handle_info(book_id)
    edited_info = json.loads(capsys.readouterr().out)
    assert edited_info["title"] == new_title
    assert edited_info["memo"] == new_memo

    # 6. 本の削除
    handle_delete(book_id)
    assert not (SHELF_DIR / book_id).exists()


# 元のテスト関数は残しておく
def test_add_book(setup_teardown):
    """本の追加機能をテスト"""
    test_pdf = Path("tests/files/test.pdf")
    book_id = "pdf_book"
    title = "PDFの本"
    memo = "pdf_book:PDFの本に関するメモ"

    handle_add(str(test_pdf), book_id, title, memo)

    # ディレクトリとファイルが作成されたことを確認
    book_dir = SHELF_DIR / book_id
    assert book_dir.exists()

    # メタデータファイルが作成されたことを確認
    json_file = book_dir / f"{book_id}.json"
    assert json_file.exists()

    # メタデータの内容を確認
    with open(json_file, encoding="utf-8") as f:
        metadata = json.load(f)

    assert metadata["id"] == book_id
    assert metadata["title"] == title
    assert metadata["memo"] == memo


def test_show_book(setup_teardown, capsys):
    """本の表示機能をテスト"""
    # 事前に本を追加
    test_pdf = Path("tests/files/test.pdf")
    book_id = "pdf_book"
    title = "PDFの本"
    memo = "pdf_book:PDFの本に関するメモ"

    handle_add(str(test_pdf), book_id, title, memo)

    # 本の内容を表示
    handle_show(book_id)

    # 標準出力をキャプチャして内容を確認
    captured = capsys.readouterr()
    assert captured.out  # 何らかの出力があることを確認


def test_info_book(setup_teardown, capsys):
    """本の情報表示機能をテスト"""
    # 事前に本を追加
    test_pdf = Path("tests/files/test.pdf")
    book_id = "pdf_book"
    title = "PDFの本"
    memo = "pdf_book:PDFの本に関するメモ"

    handle_add(str(test_pdf), book_id, title, memo)

    # 本の情報を表示
    handle_info(book_id)

    # 標準出力をキャプチャして内容を確認
    captured = capsys.readouterr()
    output = json.loads(captured.out)

    assert output["id"] == book_id
    assert output["title"] == title
    assert output["memo"] == memo


def test_edit_book(setup_teardown):
    """本の編集機能をテスト"""
    # 事前に本を追加
    test_pdf = Path("tests/files/test.pdf")
    book_id = "pdf_book"
    title = "PDFの本"
    memo = "pdf_book:PDFの本に関するメモ"

    handle_add(str(test_pdf), book_id, title, memo)

    # 本の情報を編集
    new_title = "newPDFの本"
    new_memo = "新しいメモ"
    handle_edit(book_id, new_title, new_memo)

    # 編集後のメタデータを確認
    json_file = SHELF_DIR / book_id / f"{book_id}.json"
    with open(json_file, encoding="utf-8") as f:
        metadata = json.load(f)

    assert metadata["title"] == new_title
    assert metadata["memo"] == new_memo


def test_delete_book(setup_teardown):
    """本の削除機能をテスト"""
    # 事前に本を追加
    test_pdf = Path("tests/files/test.pdf")
    book_id = "pdf_book"
    title = "PDFの本"
    memo = "pdf_book:PDFの本に関するメモ"

    handle_add(str(test_pdf), book_id, title, memo)

    # 本のディレクトリが存在することを確認
    book_dir = SHELF_DIR / book_id
    assert book_dir.exists()

    # 本を削除
    handle_delete(book_id)

    # 本のディレクトリが削除されたことを確認
    assert not book_dir.exists()


def test_list_books(setup_teardown, capsys):
    """本のリスト表示機能をテスト"""
    # 複数の本を追加
    handle_add("tests/files/test.pdf", "pdf_book", "PDFの本", "PDFのメモ")
    handle_add("tests/files/test.txt", "txt_book", "テキストの本", "テキストのメモ")

    # 本のリストを表示
    handle_list()

    # 標準出力をキャプチャして内容を確認
    captured = capsys.readouterr()

    # CSVヘッダーと2つの本のエントリがあることを確認
    lines = captured.out.strip().split("\n")
    assert len(lines) == 3  # ヘッダー + 2つの本
    assert "id,title,memo,created_at,updated_at" in lines[0]
    assert "pdf_book" in captured.out
    assert "txt_book" in captured.out


def test_full_workflow(setup_teardown, capsys):
    """memo.txtに記載されたワークフローをテスト"""
    # 1. 本の追加
    test_pdf = Path("tests/files/test.pdf")
    book_id = "pdf_book"
    title = "PDFの本"
    memo = "pdf_book:PDFの本に関するメモ"

    handle_add(str(test_pdf), book_id, title, memo)

    # 2. 本の内容表示
    handle_show(book_id)
    show_output = capsys.readouterr().out
    assert show_output  # 何らかの出力があることを確認

    # 3. 本の情報表示
    handle_info(book_id)
    info_output = json.loads(capsys.readouterr().out)
    assert info_output["title"] == title

    # 4. 本の情報編集
    new_title = "newPDFの本"
    new_memo = "新しいメモ"
    handle_edit(book_id, new_title, new_memo)

    # 5. 編集後の情報表示
    handle_info(book_id)
    edited_info = json.loads(capsys.readouterr().out)
    assert edited_info["title"] == new_title
    assert edited_info["memo"] == new_memo

    # 6. 本の削除
    handle_delete(book_id)
    assert not (SHELF_DIR / book_id).exists()
