"""Render the alphabetical writing collection from its source catalog."""

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = [
    "Anti-slop writing",
    "Copywriting and sales",
    "Blogs and articles",
    "Email and newsletters",
    "Social posts and scripts",
    "UGC and video scripting",
    "Video platform workflows",
    "Editing and voice",
    "Specialist and house styles",
    "Languages",
    "Linters and pattern checkers",
    "Research and further reading",
]


def load_catalog():
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    if catalog["schema_version"] != 1:
        raise ValueError("Unsupported catalog schema")
    entries = catalog["entries"]
    for key in ("id", "url"):
        if len({entry[key] for entry in entries}) != len(entries):
            raise ValueError(f"Duplicate catalog {key}")
    for entry in entries:
        if entry["category"] not in CATEGORIES:
            raise ValueError(f"Unknown category: {entry['category']}")
        if not re.fullmatch(r"[0-9a-f]{64}", entry["source_sha256"]):
            raise ValueError(f"Invalid source checksum: {entry['id']}")
        if entry["repo"]:
            revision = entry["source_revision"]
            if not re.fullmatch(r"[0-9a-f]{40}", revision or ""):
                raise ValueError(f"Missing source revision: {entry['id']}")
            expected = f"https://github.com/{entry['repo']}/blob/{revision}/{entry['path']}"
            if entry["source_url"] != expected:
                raise ValueError(f"Source URL does not match revision: {entry['id']}")
    return entries


def render(entries):
    lines = [
        "# Awesome Anti-Slop",
        "",
        "A collection of writing skills, prompts, linters and research: anti-slop editing, copywriting, blogs, email, newsletters, social posts, UGC and video scripts.",
        "",
        f"{len(entries)} resources. Alphabetical within each category. No rankings or recommendations.",
        "",
        "The collection comes first. The next stage is an amalgamation of the collected methods, with attribution and conflicting rules kept visible. Sources remain separate here so that work can be traced back to their authors.",
        "",
        "[catalog.json](catalog.json) contains source URLs, pinned Git revisions, checksums, inspection dates and repository license metadata. Descriptions reflect inspected entry files or documentation; inclusion does not claim tested effectiveness.",
        "",
        "## Contents",
        "",
    ]
    for category in CATEGORIES:
        lines.append(f"- [{category}](#{category.lower().replace(' ', '-')})")
    lines += ["- [Collection and provenance](#collection-and-provenance)", "- [Contributing](#contributing)", ""]
    for category in CATEGORIES:
        lines += [f"## {category}", ""]
        members = sorted(
            (entry for entry in entries if entry["category"] == category),
            key=lambda entry: entry["title"].lower(),
        )
        for entry in members:
            lines.append(f"- [{entry['title']}]({entry['url']}) - {entry['description']}")
        lines.append("")
    lines += [
        "## Collection and provenance",
        "",
        "The catalog includes individual skills, multi-skill repositories, prompts, linters and research. Video entries distinguish script and prompt guidance from production/API workflows. Platform-published and community resources are identified in their descriptions; support for a platform does not imply that platform authored the resource. A repository containing many skills counts as one resource when collected at repository level. Separate skill entries identify their paths. This is an expanding collection, not an exhaustive inventory.",
        "",
        "Related projects can share rules, translations or source material. Their entries remain distinct. `related_sources` records relationships stated in inspected sources; it is not a complete genealogy. A GitHub fork flag alone would miss adaptations copied into separate repositories.",
        "",
        "GitHub sources have a pinned revision and a SHA-256 checksum of the retrieved entry file. A non-Git source has a retrieval date and checksum without a revision pin. These records identify what was retrieved; they do not certify a complete review of every referenced file or bundled skill.",
        "",
        "License fields come from GitHub's repository metadata. A missing value means no license was detected there. File-specific terms and dependencies still need inspection before an amalgamation incorporates upstream text. This collection links to source material without republishing it.",
        "",
        "Discovery has included GitHub and web searches, [Awesome Humanizer Skills](https://github.com/zhuyansen/awesome-humanizer-skills) and the [AI Writing Skill Field Guide](https://github.com/Daguilar0123/ai-writing-skill-field-guide). Their rankings and assessments are not adopted here.",
        "",
        "## Contributing",
        "",
        "Open an issue with a source URL, or add a record to `catalog.json` in a pull request. Include the author, category, a neutral description, inspected source URL, revision where available, checksum, inspection date and license metadata. For an adaptation, record its stated sources. Do not add rankings, endorsements or performance claims without attribution.",
        "",
        "Scope includes writing, editing, research for writing, voice, scripts, correspondence and content planning across languages. General-purpose apps and code/UI-only cleanup tools are outside this collection; interface writing is in scope.",
        "",
        "Run `python3 scripts/render.py` after editing the catalog, then `mise run check`. The checks validate catalog records, README freshness, whitespace, links and section anchors. They make public HTTP requests but do not install or execute any collected skill.",
        "",
        "## License",
        "",
        "This collection's original descriptions are dedicated to the public domain under [CC0 1.0](LICENSE). Linked projects retain their own licenses.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = render(load_catalog())
    path = ROOT / "README.md"
    if args.check:
        if path.read_text(encoding="utf-8") != output:
            parser.exit(1, "README is stale; run python3 scripts/render.py\n")
        print("Catalog valid; README matches catalog.")
    else:
        path.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
