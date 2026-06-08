"""
Task 3 - Convert files in data/landing/ to Markdown.

Legal documents are converted with Microsoft's MarkItDown. Crawled news JSON
files are normalized to Markdown while preserving article metadata.
"""

import json
from pathlib import Path

from markitdown import MarkItDown

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"

SUPPORTED_MARKITDOWN_EXTENSIONS = {".pdf", ".docx", ".doc", ".html", ".htm", ".txt"}


def safe_text(value: object) -> str:
    """Return console-safe text for Windows terminals with legacy encodings."""
    return str(value).encode("ascii", errors="replace").decode("ascii")


def output_path_for(input_path: Path) -> Path:
    """Map data/landing/<subdir>/file.ext to data/standardized/<subdir>/file.md."""
    relative_path = input_path.relative_to(LANDING_DIR)
    return (OUTPUT_DIR / relative_path).with_suffix(".md")


def write_markdown(output_path: Path, content: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"  Saved: {safe_text(output_path)}")


def convert_with_markitdown(filepath: Path, md: MarkItDown) -> str:
    """Convert one file with MarkItDown and return extracted markdown text."""
    result = md.convert(str(filepath))
    content = getattr(result, "text_content", "") or ""
    if not content.strip():
        raise ValueError(f"MarkItDown returned empty content for {filepath}")
    return content


def convert_legal_docs() -> list[Path]:
    """Convert PDF/DOC/DOCX files in data/landing/legal/ to Markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_files: list[Path] = []
    if not legal_dir.exists():
        print(f"Legal directory not found: {legal_dir}")
        return output_files

    md = MarkItDown()
    for filepath in sorted(legal_dir.iterdir()):
        if not filepath.is_file() or filepath.suffix.lower() not in SUPPORTED_MARKITDOWN_EXTENSIONS:
            continue

        print(f"Converting legal: {safe_text(filepath.name)}")
        output_path = output_path_for(filepath)
        content = convert_with_markitdown(filepath, md)
        header = f"# {filepath.stem}\n\n**Source file:** `{filepath.name}`\n\n---\n\n"
        write_markdown(output_path, header + content)
        output_files.append(output_path)

    return output_files


def convert_news_articles() -> list[Path]:
    """Convert crawled article JSON files in data/landing/news/ to Markdown."""
    news_dir = LANDING_DIR / "news"
    output_files: list[Path] = []
    if not news_dir.exists():
        print(f"News directory not found: {news_dir}")
        return output_files

    for filepath in sorted(news_dir.iterdir()):
        if not filepath.is_file() or filepath.suffix.lower() != ".json":
            continue

        print(f"Converting news: {safe_text(filepath.name)}")
        data = json.loads(filepath.read_text(encoding="utf-8"))
        title = data.get("title") or filepath.stem
        url = data.get("url", "N/A")
        date_crawled = data.get("date_crawled", "N/A")
        crawler = data.get("crawler", "N/A")
        content_markdown = data.get("content_markdown") or data.get("content") or ""
        if not content_markdown.strip():
            raise ValueError(f"News JSON has no content: {filepath}")

        markdown = (
            f"# {title}\n\n"
            f"**Source:** {url}\n\n"
            f"**Crawled:** {date_crawled}\n\n"
            f"**Crawler:** {crawler}\n\n"
            "---\n\n"
            f"{content_markdown}"
        )
        output_path = output_path_for(filepath)
        write_markdown(output_path, markdown)
        output_files.append(output_path)

    return output_files


def convert_other_landing_files() -> list[Path]:
    """Convert supported files outside legal/news while preserving subfolders."""
    md = MarkItDown()
    output_files: list[Path] = []
    for filepath in sorted(LANDING_DIR.rglob("*")):
        if not filepath.is_file() or filepath.name.startswith("."):
            continue
        if "legal" in filepath.relative_to(LANDING_DIR).parts:
            continue
        if "news" in filepath.relative_to(LANDING_DIR).parts:
            continue
        if filepath.suffix.lower() not in SUPPORTED_MARKITDOWN_EXTENSIONS:
            continue

        print(f"Converting file: {safe_text(filepath.name)}")
        output_path = output_path_for(filepath)
        content = convert_with_markitdown(filepath, md)
        write_markdown(output_path, content)
        output_files.append(output_path)

    return output_files


def convert_all() -> list[Path]:
    """Convert all supported landing files into data/standardized/."""
    print("=" * 50)
    print("Task 3: Convert to Markdown with MarkItDown")
    print("=" * 50)

    output_files: list[Path] = []
    print("\n--- Legal Documents ---")
    output_files.extend(convert_legal_docs())

    print("\n--- News Articles ---")
    output_files.extend(convert_news_articles())

    print("\n--- Other Files ---")
    output_files.extend(convert_other_landing_files())

    print(f"\nDone. Wrote {len(output_files)} markdown files to: {OUTPUT_DIR}")
    return output_files


if __name__ == "__main__":
    convert_all()
