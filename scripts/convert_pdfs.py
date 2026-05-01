import pymupdf4llm
import pathlib
import re
import sys

DOCS_DIR = pathlib.Path(__file__).parent.parent / "docs"
DOCS_DIR.mkdir(exist_ok=True)


def slugify(name: str) -> str:
    name = name.lower().replace(" ", "-")
    name = re.sub(r"[^\w\-]", "", name)
    return name


def convert(pdf_path: pathlib.Path) -> pathlib.Path:
    md_text = pymupdf4llm.to_markdown(str(pdf_path))
    out = DOCS_DIR / (slugify(pdf_path.stem) + ".md")
    out.write_text(md_text, encoding="utf-8")
    return out


if __name__ == "__main__":
    if sys.argv[1:]:
        arg = pathlib.Path(sys.argv[1])
        targets = sorted(p for p in arg.iterdir() if p.suffix.lower() == ".pdf") if arg.is_dir() else [arg]
    else:
        print("Usage: convert_pdfs.py <pdf-dir-or-file>")
        sys.exit(1)

    for pdf in targets:
        out = DOCS_DIR / (slugify(pdf.stem) + ".md")
        if out.exists():
            print(f"SKIP {pdf.name}")
            continue
        try:
            out = convert(pdf)
            print(f"OK  {pdf.name} → {out.name}")
        except Exception as e:
            print(f"ERR {pdf.name}: {e}", file=sys.stderr)
