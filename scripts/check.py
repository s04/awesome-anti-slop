"""Check this collection's Markdown links using only the standard library."""

import concurrent.futures
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

from render import DOCUMENTS

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


def anchors(source):
    headings = re.findall(r"^#+ (.+)$", source, re.MULTILINE)
    return {
        re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        for heading in headings
    }
def collect_links(documents):
    urls, errors = set(), []
    for path in documents:
        source = path.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", source):
            if link.startswith("https://"):
                urls.add(link)
                continue
            relative, _, fragment = link.partition("#")
            target = path.parent / relative if relative else path
            if not target.is_file():
                errors.append(f"{path}: Missing local file: {link}")
            elif fragment and fragment not in anchors(target.read_text(encoding="utf-8")):
                errors.append(f"{path}: Missing section: {link}")
    return sorted(urls), errors


def main():
    urls, errors = collect_links([ROOT / name for name in DOCUMENTS])
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        errors.extend(error for error in pool.map(check_url, urls) if error)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Passed: {len(urls)} external URLs, local links and section anchors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
