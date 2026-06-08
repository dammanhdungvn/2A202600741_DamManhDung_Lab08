"""
Task 1 - Collect legal documents about drugs and controlled substances.

Downloads official PDF documents from Cong Bao Chinh Phu into
data/landing/legal/ with clear, ASCII filenames.
"""

from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import urljoin
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


@dataclass(frozen=True)
class LegalDocument:
    title: str
    url: str
    filename: str


LEGAL_DOCUMENTS = [
    LegalDocument(
        title="Luat Phong, chong ma tuy 2021 - Luat so 73/2021/QH14",
        url="https://congbao.chinhphu.vn/tai-ve-van-ban-so-73-2021-qh14-33659-35652?format=pdf",
        filename="luat-phong-chong-ma-tuy-2021.pdf",
    ),
    LegalDocument(
        title="Nghi dinh 105/2021/ND-CP huong dan Luat Phong, chong ma tuy",
        url="https://congbao.chinhphu.vn/tai-ve-van-ban-so-105-2021-nd-cp-34944-37821?format=pdf",
        filename="nghi-dinh-105-2021-huong-dan-luat-phong-chong-ma-tuy.pdf",
    ),
    LegalDocument(
        title="Nghi dinh 57/2022/ND-CP quy dinh danh muc chat ma tuy va tien chat",
        url="https://congbao.chinhphu.vn/tai-ve-van-ban-so-57-2022-nd-cp-37734-41623?format=pdf",
        filename="nghi-dinh-57-2022-danh-muc-chat-ma-tuy-va-tien-chat.pdf",
    ),
]


def setup_directory() -> None:
    """Create data/landing/legal/ if it does not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Directory ready: {DATA_DIR}")


def is_valid_document(content: bytes, filename: str) -> bool:
    """Basic guard to avoid saving an HTML error page as a legal document."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return content.startswith(b"%PDF")
    if suffix == ".docx":
        return content.startswith(b"PK")
    if suffix == ".doc":
        return content.startswith(b"\xd0\xcf\x11\xe0")
    return False


def extract_document_url(html_content: bytes, base_url: str, suffix: str) -> str | None:
    """Find the first PDF/DOC/DOCX URL embedded in a Cong Bao HTML page."""
    text = html_content.decode("utf-8", errors="replace")
    escaped_suffix = re.escape(suffix.lower())
    patterns = [
        rf'data-href="([^"]+?{escaped_suffix})"',
        rf"data-href='([^']+?{escaped_suffix})'",
        rf'href="([^"]+?{escaped_suffix})"',
        rf"href='([^']+?{escaped_suffix})'",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return urljoin(base_url, match.group(1))
    return None


def fetch_url(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=60) as response:
        return response.read()


def download_file(document: LegalDocument, overwrite: bool = False) -> Path:
    """
    Download one legal document and save it under DATA_DIR.

    Existing non-empty files are kept by default to avoid unnecessary downloads.
    """
    setup_directory()
    filepath = DATA_DIR / document.filename

    if filepath.exists() and filepath.stat().st_size > 1024 and not overwrite:
        print(f"Skip existing file: {filepath.name}")
        return filepath

    try:
        content = fetch_url(document.url)
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Cannot download {document.title}: {exc}") from exc

    if not is_valid_document(content, document.filename):
        suffix = Path(document.filename).suffix
        embedded_url = extract_document_url(content, document.url, suffix)
        if embedded_url:
            try:
                content = fetch_url(embedded_url)
            except (HTTPError, URLError) as exc:
                raise RuntimeError(f"Cannot download embedded file for {document.title}: {exc}") from exc

    if len(content) <= 1024:
        raise ValueError(f"Downloaded file is too small: {document.filename}")
    if not is_valid_document(content, document.filename):
        raise ValueError(f"Downloaded content is not a valid document: {document.filename}")

    filepath.write_bytes(content)
    print(f"Downloaded: {filepath.name} ({len(content):,} bytes)")
    return filepath


def download_all(overwrite: bool = False) -> list[Path]:
    """Download all configured legal documents."""
    setup_directory()
    downloaded = []
    for document in LEGAL_DOCUMENTS:
        downloaded.append(download_file(document, overwrite=overwrite))
    return downloaded


if __name__ == "__main__":
    files = download_all()
    print(f"Done. Legal documents available: {len(files)}")
