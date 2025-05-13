# My Shelf - 本棚管理システム

シンプルなコマンドラインベースの本棚管理システムです。PDF、EPUB、テキストファイルを管理し、それらのテキスト内容を抽出して保存します。

## 機能

- 本（PDF、EPUB、テキスト）の追加
- 本の内容表示
- 本のメタデータ編集
- 本の削除
- 本棚内の全ての本のリスト表示

## 必要条件

- Python 3.13以上
- uv（Python パッケージマネージャー）
- 依存ライブラリ:
  - PyMuPDF (PDF処理用)
  - EbookLib (EPUB処理用)
  - BeautifulSoup4 (HTML解析用)

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/my-shelf.git
cd my-shelf

# uvを使って依存関係をインストール
uv sync

# または以下のようにuvでインストールすることも可能
uv pip install -e .
```

## ビルド

Makefileを使用して簡単にビルドできます：

```bash
# 実行ファイルのビルド
make build

# テストの実行
make test

# 型チェック
make typecheck

# リンター実行
make lint

# コードフォーマット
make format

# クリーンアップ
make clean
```

## 使い方

### 本の追加

```bash
shelf add book.pdf "book_id" "本のタイトル" --memo "この本に関するメモ"
```

### 本の内容表示

```bash
shelf show book_id
```

### 本のメタデータ編集

```bash
shelf edit book_id --title "新しいタイトル" --memo "新しいメモ"
```

### 本の削除

```bash
shelf delete book_id
```

### 本棚の一覧表示

```bash
shelf list
```

## ディレクトリ構造

```
shelf/
├── book_a/
│   ├── book_a.json  # メタデータ
│   ├── book_a.pdf   # 元のファイル
│   └── book_a.txt   # 抽出されたテキスト
├── book_b/
│   ├── book_b.epub
│   ├── book_b.json
│   └── book_b.txt
└── book_c/
    ├── book_c.json
    └── book_c.txt
```
