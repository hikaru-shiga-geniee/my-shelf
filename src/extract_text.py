import fitz  # PyMuPDF
from pathlib import Path
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import logging  # logging をインポート

# モジュールレベルでロガーを取得
logger = logging.getLogger(__name__)


def extract_text_from_pdf(path: Path) -> str | None:
    """
    指定されたPDFファイルからテキストを抽出します。

    PyMuPDFライブラリを使用して、PDFファイルの各ページからテキストコンテンツを
    取り出します。抽出中にエラーが発生した場合は、標準エラーに英語で
    エラーメッセージを出力し、Noneを返します。

    Args:
        path (Path): 読み込むPDFファイルのパス。

    Returns:
        str | None: 抽出されたテキスト全体。エラーが発生した場合はNone。
    """
    text = ""
    try:
        with fitz.open(path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text("text")
        return text
    except Exception as e:
        # print の代わりに logger.error を使用
        # exc_info=True で例外情報（スタックトレース）もログに出力
        logger.error(
            f"Error occurred while processing PDF '{path}': {e}", exc_info=True
        )
        return None


def extract_text_from_epub(path: Path) -> str | None:
    """
    指定されたEPUBファイルからプレーンテキストを抽出します。

    EbookLibライブラリでEPUBファイルを読み込み、BeautifulSoupライブラリを
    使用して各ドキュメント（主にXHTML）からHTMLタグを除去し、テキストのみを
    抽出します。抽出中にエラーが発生した場合は、標準エラーに英語で
    エラーメッセージを出力し、Noneを返します。

    Args:
        path (Path): 読み込むEPUBファイルのパス。

    Returns:
        str | None: 抽出されたテキスト全体。エラーが発生した場合はNone。
    """
    full_text = ""
    try:
        book = epub.read_epub(path, options={"ignore_ncx": True})
        items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)

        for item in items:
            content_bytes = item.get_content()
            html_content = content_bytes.decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text()
            full_text += text + ""
        return full_text

    except FileNotFoundError:  # FileNotFoundError も Exception の一種だが、個別でログメッセージを変えても良い
        # print の代わりに logger.error を使用
        logger.error(
            f"Error: File not found: {path}", exc_info=True
        )  # FileNotFoundError では通常スタックトレースは不要かもしれないが、付けておいても問題ない
        return None
    except epub.EpubException as e:  # ebooklib.epub.EpubException から epub.EpubException に変更
        # print の代わりに logger.error を使用
        logger.error(f"Error: Failed to read EPUB file ({path}): {e}", exc_info=True)
        return None
    except Exception as e:
        # print の代わりに logger.error を使用
        logger.error(
            f"An unexpected error occurred while processing EPUB '{path}': {e}",
            exc_info=True,
        )
        return None


# パターンマッチ構文を使用した extract_text 関数
def extract_text(path: Path) -> str | None:
    """
    指定されたファイルの拡張子に基づいて適切なテキスト抽出関数を呼び出します。(パターンマッチ使用)

    ファイルの拡張子が '.pdf' または '.epub' (大文字小文字を区別しない) の場合、
    対応する抽出関数 (`extract_text_from_pdf` または `extract_text_from_epub`)
    を呼び出します。サポートされていないファイルタイプの場合は警告をログに出力し、
    Noneを返します。

    Args:
        path (Path): 読み込むファイルのパス。

    Returns:
        str | None: 抽出されたテキスト全体。
                    サポートされていないファイルタイプ、または抽出中にエラーが
                    発生した場合はNone。
    """
    # ファイルの拡張子を小文字で取得
    suffix = path.suffix.lower()

    # match-case で拡張子に基づいて処理を分岐
    match suffix:
        case ".pdf":
            logger.info(f"Processing PDF file: {path}")
            return extract_text_from_pdf(path)
        case ".epub":
            logger.info(f"Processing EPUB file: {path}")
            return extract_text_from_epub(path)
        case ".txt":
            logger.info(f"Processing TXT file: {path}")
            return path.read_text()
        case _:  # ワイルドカードパターン: 上記のcaseに一致しない場合
            logger.warning(
                f"Unsupported file type: '{path.suffix}' for file '{path}'. Only .pdf and .epub are supported."
            )
            return None 