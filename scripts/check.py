"""Check this collection's Markdown links using only the standard library."""

import concurrent.futures
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parent.parent


def check_url(url):
    target = url
    # Check the source file directly instead of GitHub's interactive page shell.
    if url.startswith("https://github.com/") and "/blob/" in url:
        target = url.replace(
            "https://github.com/", "https://raw.githubusercontent.com/", 1
        ).replace("/blob/", "/", 1)
    request = urllib.request.Request(
        target, headers={"User-Agent": "awesome-anti-slop-link-check"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                return f"{url}: HTTP {response.status}"
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return f"{url}: {error}"
    return None


def main():
    source = (ROOT / "README.md").read_text(encoding="utf-8")
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", source)
    headings = re.findall(r"^#+ (.+)$", source, re.MULTILINE)
    anchors = {
        re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        for heading in headings
    }
    errors = []
    for link in links:
        if link.startswith("#"):
            if link[1:] not in anchors:
                errors.append(f"Missing section: {link}")
        elif not link.startswith("https://"):
            if not (ROOT / link).is_file():
                errors.append(f"Missing local file: {link}")
    urls = sorted({link for link in links if link.startswith("https://")})
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        errors.extend(error for error in pool.map(check_url, urls) if error)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Passed: {len(urls)} external URLs, local links and section anchors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
