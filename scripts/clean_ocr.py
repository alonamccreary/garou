import pathlib, re

DOCS_DIR = pathlib.Path('docs')
NL = chr(10)

# Common short English words that are legitimate
COMMON_WORDS = set('a an the and or but in on at to of for is it its are was were be been has have had '
                   'with from by this that he she we they you I do not no so if as up '
                   'his her our my all one two can will would could should may might '
                   'then when who what where there their them than just out more'.split())

def letter_ratio(text):
    non_ws = text.replace(' ', '')
    if not non_ws:
        return 1.0
    return sum(1 for c in non_ws if c.isalpha()) / len(non_ws)

def word_legitimacy(text):
    """Ratio of words that look like real English words."""
    words = text.split()
    if not words:
        return 1.0
    legit = 0
    for w in words:
        w_clean = re.sub(r'[^a-zA-Z]', '', w).lower()
        if not w_clean:
            continue
        if w_clean in COMMON_WORDS:
            legit += 1
        elif len(w_clean) >= 4 and letter_ratio(w_clean) == 1.0:
            # Long all-letter word - likely real
            legit += 0.5
    return legit / len(words)

def is_garbled_paragraph(para):
    """Return True if this paragraph block should be removed."""
    if not para.strip():
        return False
    lines = para.strip().splitlines()
    # Skip headers and markdown structure
    if all(l.strip().startswith(('#', '---', '|', '>')) for l in lines if l.strip()):
        return False
    text = ' '.join(lines)
    lr = letter_ratio(text)
    wl = word_legitimacy(text)
    # Garbled if: low letter ratio OR very low word legitimacy
    if lr < 0.60:
        return True
    if wl < 0.08 and len(text) > 30:
        return True
    return False

def remove_picture_text(text):
    text = re.sub(r'==>.*?<==.*?' + NL, '', text)
    text = re.sub(
        r'----- Start of picture text -----.*?----- End of picture text -----' + NL + '?',
        '', text, flags=re.DOTALL)
    return text

def clean_file(path):
    text = path.read_text(encoding='utf-8')
    orig_lines = text.count(NL)
    text = remove_picture_text(text)
    # Split into paragraphs (blank-line separated)
    paragraphs = re.split(r'(' + NL + r'{2,})', text)
    cleaned = []
    removed_lines = 0
    in_code = False
    for chunk in paragraphs:
        if chunk.strip().startswith('```') or in_code:
            in_code = not chunk.strip().endswith('```') or in_code
            cleaned.append(chunk)
            continue
        if re.fullmatch(r'(' + NL + r'+)', chunk):
            cleaned.append(chunk)
            continue
        if is_garbled_paragraph(chunk):
            removed_lines += chunk.count(NL) + 1
        else:
            cleaned.append(chunk)
    result = ''.join(cleaned)
    result = re.sub(NL + '{3,}', NL * 2, result)
    path.write_text(result, encoding='utf-8')
    return orig_lines, removed_lines

if __name__ == '__main__':
    total = 0
    for md in sorted(DOCS_DIR.glob('*.md')):
        if md.name == 'index.md':
            continue
        orig, removed = clean_file(md)
        if removed:
            pct = removed * 100 // max(orig, 1)
            print(f'{md.name}: removed ~{removed}/{orig} lines ({pct}%)')
            total += removed
    print(f'Done. Total lines removed: {total}')
