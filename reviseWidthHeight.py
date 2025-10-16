import re
import shutil
from pathlib import Path

# --- CONFIG ---
FOLDER = r"C:\Users\Owner\Documents\GitHub\Utah-Idaho_pics"   # <- change this
WIDTH, HEIGHT = 600, 900
RECURSE = True            # set to False to only process the top-level folder
MAKE_BACKUPS = True       # creates filename.html.bak beside each edited file
ENCODING = "utf-8"        # change if your files use a different encoding

# --- Regexes ---
# Match any <img ...> tag (case-insensitive), minimal to the next '>'
IMG_TAG_RE = re.compile(r"<img\b[^>]*?>", re.IGNORECASE | re.DOTALL)

# Remove any width=... or height=... attribute inside an <img> tag (any quotes/values)
DIM_RE = re.compile(r"\s*(?:width|height)\s*=\s*(['\"]).*?\1", re.IGNORECASE | re.DOTALL)

def rewrite_img_tag(tag: str) -> str:
    """
    Return the tag with width/height stripped and then set to WIDTH/HEIGHT.
    Preserves all other attributes and the original closing style (">" or "/>").
    """
    # Strip any width/height attrs
    cleaned = DIM_RE.sub("", tag)

    # Split off the closing '>' or '/>'
    m = re.match(r"^(.*?)(/?>)$", cleaned, flags=re.DOTALL)
    head, close = (m.group(1), m.group(2)) if m else (cleaned, ">")

    # Normalize spacing a bit (without touching attribute values)
    head = re.sub(r"\s+", " ", head).rstrip()

    # Ensure there's a space before adding new attributes
    if not head.endswith("<img") and not head.endswith("<IMG"):
        head += " "

    # Inject the desired dimensions (width first, then height)
    return f'{head}width="{WIDTH}" height="{HEIGHT}"{close}'

def process_file(path: Path) -> bool:
    text = path.read_text(encoding=ENCODING, errors="ignore")

    # Replace all <img> tags using the rewrite function
    new_text, n = IMG_TAG_RE.subn(lambda m: rewrite_img_tag(m.group(0)), text)

    if n > 0 and new_text != text:
        if MAKE_BACKUPS:
            bak = path.with_suffix(path.suffix + ".bak")  # e.g., file.html.bak
            if not bak.exists():
                shutil.copy2(path, bak)
        path.write_text(new_text, encoding=ENCODING)
        print(f"Updated ({n} tag(s)): {path}")
        return True
    return False

def main():
    root = Path(FOLDER)
    if RECURSE:
        files = list(root.rglob("*.html"))
    else:
        files = list(root.glob("*.html"))

    changed = 0
    for p in files:
        if process_file(p):
            changed += 1
    print(f"\nDone. Files modified: {changed}/{len(files)}")

if __name__ == "__main__":
    main()
