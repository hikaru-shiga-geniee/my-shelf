# tests/test_convert_txt.py
from pathlib import Path

# Import the function to be tested
# Assuming your function is in 'convert_txt.py' and named 'extract_text_from_pdf'
# 注意: 以下のimportが成功するには、プロジェクトのルートディレクトリからpytestを実行するか、
# PYTHONPATHにsrcディレクトリが含まれている必要があります。
# (現在のpytestの実行方法では問題ないはずです)
from extract_text import extract_text_from_pdf, extract_text_from_epub

# --- Pytest Fixtures ---


def test_extract_text_from_pdf():
    path = Path("tests/files/test.pdf")
    txt = extract_text_from_pdf(path)
    assert txt is not None


def test_extract_text_from_epub():
    path = Path("tests/files/test.epub")
    txt = extract_text_from_epub(path)
    assert txt is not None
