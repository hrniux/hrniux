"""Check local inline README links/images and SVG syntax; no external requests.

Supported Markdown is inline [label](destination) and HTML href/src attributes.
This is a local asset check, not a complete Markdown parser or remote link check.
"""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for name in ("href", "src"):
            if name in attrs:
                self.targets.append(attrs[name] or "")
        if tag == "img" and not (attrs.get("alt") or "").strip():
            self.errors.append("HTML image needs nonempty alt text")


def check_profile(root):
    root = Path(root).resolve()
    try:
        text = (root / "README.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return [f"README.md: {error}"]
    parser = References()
    parser.feed(text)
    errors = list(parser.errors)
    inline = re.findall(r'(!?)\[([^\]]*)\]\(([^\s)]+)(?:\s+"[^"]*")?\)', text)
    targets = list(parser.targets)
    for image, label, target in inline:
        targets.append(target)
        if image and not label.strip():
            errors.append("Markdown image needs nonempty alt text")
    for target in sorted(set(targets)):
        url = urlsplit(target)
        if url.scheme or url.netloc or not url.path:
            continue
        local = (root / unquote(url.path).lstrip("/")).resolve()
        if not local.is_relative_to(root):
            errors.append(f"Local link points outside repository: {target}")
        elif not local.exists():
            errors.append(f"Missing local target: {target}")
    for svg in sorted((root / "assets").rglob("*.svg")):
        if not svg.resolve().is_relative_to(root):
            errors.append(f"SVG outside repository: {svg.relative_to(root)}")
            continue
        try:
            element = ET.parse(svg).getroot()
            if element.tag != "{http://www.w3.org/2000/svg}svg":
                errors.append(f"Invalid SVG root: {svg.relative_to(root)}")
        except (OSError, ET.ParseError) as error:
            errors.append(f"SVG {svg.relative_to(root)}: {error}")
    return errors


if __name__ == "__main__":
    errors = check_profile(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Profile local asset check: {len(errors)} error(s); external URLs not checked")
    raise SystemExit(bool(errors))
