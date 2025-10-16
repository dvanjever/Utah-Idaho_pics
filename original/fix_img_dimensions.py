import re
import shutil
from pathlib import Path

# --- CONFIG ---
WIDTH, HEIGHT = 320, 480
RECURSE = True           # set False to process only the current folder
MAKE_BACKUPS = True      # create .bak backup files
ENCODING = "utf-8"       # adjust if needed

# --- Regexes ---
IMG_TAG_RE = re.compile(r"<img\b[^>]*?>", re.IGNORECASE | re.DOTALL)
DIM_RE = re.compile(r"\s*(?:width|height)\s*=\s*(['\"]).*?\1", re.IGNORECASE | re.DOTALL)

def rewrite_img_tag(tag: str) -> str:
    """Remove existing width/height and add the new ones."""
    cleaned = DIM_RE.sub("", tag)
    m = re.match(r"^(.*?)(/?>)$", cleaned, flags=re.DOTALL)
    head, close = (m.group(1), m.group(2)) if m else (cleaned, ">")
    head = re.sub(r"\s+", " ", head).rstrip()
    if not head.endswith("<img") and not head.endswith("<IMG"):
        head += " "
    return f'{head}width="{WIDTH}" height="{HEIGHT}"{close}'

def process_file(path: Path) -> bool:
    text = path.read_text(encoding=ENCODING, errors="ignore")
    new_text, n = IMG_TAG_RE.subn(lambda m: rewrite_img_tag(m.group(0)), text)
    if n > 0 and new_text != text:
        if MAKE_BACKUPS:
            bak = path.with_suffix(path.suffix + ".bak")
            if not bak.exists():
                shutil.copy2(path, bak)
        path.write_text(new_text, encoding=ENCODING)
        print(f"Updated ({n} <img> tag(s)): {path}")
        return True
    return False

def main():
    root = Path.cwd()  # use the directory where the script is run
    files = root.rglob("*.html") if RECURSE else root.glob("*.html")
    changed = sum(1 for p in files if process_file(p))
    print(f"\nDone. Files modified: {changed}")

if __name__ == "__main__":
    main()
