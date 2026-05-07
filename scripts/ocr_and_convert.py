import pathlib, re, subprocess, tempfile
import pymupdf4llm

PDF_DIR = pathlib.Path('/mnt/c/Users/laura/OneDrive/Documents/LARP Books')
DOCS_DIR = pathlib.Path(__file__).parent.parent / 'docs'
WORD_THRESHOLD = 100

def slugify(name):
    name = name.lower().replace(' ', '-')
    return re.sub(r'[^\w\-]', '', name)

def word_count(path):
    try:
        return len(path.read_text(encoding='utf-8').split())
    except FileNotFoundError:
        return 0

def needs_ocr(pdf):
    return word_count(DOCS_DIR / (slugify(pdf.stem) + '.md')) < WORD_THRESHOLD

def ocr_pdf(src, dst):
    subprocess.run(['ocrmypdf', '--skip-text', '--optimize', '0', '--invalidate-digital-signatures', str(src), str(dst)], check=True, capture_output=True)

def convert(pdf):
    md_text = pymupdf4llm.to_markdown(str(pdf))
    out = DOCS_DIR / (slugify(pdf.stem) + '.md')
    out.write_text(md_text, encoding='utf-8')
    return out

if __name__ == '__main__':
    pdfs = sorted(p for p in PDF_DIR.iterdir() if p.suffix.lower() == '.pdf')
    to_process = [p for p in pdfs if needs_ocr(p)]
    print(f'Found {len(to_process)} PDFs needing OCR:')
    for p in to_process:
        print(f'  {p.name}')
    print()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        for pdf in to_process:
            print(f'OCR  {pdf.name} ...', end=' ', flush=True)
            try:
                ocr_out = tmp / pdf.name
                ocr_pdf(pdf, ocr_out)
                md = convert(ocr_out)
                print(f'OK ({word_count(md)} words -> {md.name})')
            except subprocess.CalledProcessError as e:
                print(f'ERR ocrmypdf: {e.stderr.decode()[:120]}')
            except Exception as e:
                print(f'ERR: {e}')
