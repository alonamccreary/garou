import pathlib, re

DOCS_DIR = pathlib.Path('docs')
LETTER_RATIO_THRESHOLD = 0.55
MIN_LINE_LENGTH = 4
NL = chr(10)

def is_garbled(line):
    stripped = line.strip()
    if not stripped:
        return False
    if stripped[0] in '#-=|>':
        return False
    non_ws = stripped.replace(' ', '')
    if len(non_ws) < MIN_LINE_LENGTH:
        return False
    letters = sum(1 for c in non_ws if c.isalpha())
    return (letters / len(non_ws)) < LETTER_RATIO_THRESHOLD

def clean_file(path):
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
    cleaned, removed = [], 0
    in_code = False
    for line in lines:
        if line.strip().startswith('```'):
            in_code = not in_code
        if in_code or not is_garbled(line):
            cleaned.append(line)
        else:
            removed += 1
    text = re.sub(NL + '{3,}', NL * 2, ''.join(cleaned))
    path.write_text(text, encoding='utf-8')
    return len(lines), removed

if __name__ == '__main__':
    total = 0
    for md in sorted(DOCS_DIR.glob('*.md')):
        if md.name == 'index.md':
            continue
        orig, removed = clean_file(md)
        if removed:
            print(f'{md.name}: removed {removed}/{orig} lines ({removed*100//orig}%)')
            total += removed
    print(f'Done. Total garbled lines removed: {total}')
