"""Render the writing collection and its UI companion from their source catalogs."""

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = [
    "Anti-slop writing",
    "Copywriting and sales",
    "Marketing and content workflows",
    "Blogs and articles",
    "Email and newsletters",
    "Social posts and scripts",
    "UGC and video scripting",
    "Video platform workflows",
    "Editing and voice",
    "Specialist and house styles",
    "Languages",
    "Linters and pattern checkers",
    "Writing guides and essays",
    "Books on writing",
    "Blogs and newsletters",
    "Author social feeds",
    "Courses and practice",
    "Research and further reading",
]
DOCUMENTS = ("README.md", "ui/README.md")


def load_catalog(path=None, categories=None):
    catalog = json.loads((path or ROOT / "catalog.json").read_text(encoding="utf-8"))
    categories = CATEGORIES if categories is None else categories
    if catalog["schema_version"] != 1:
        raise ValueError("Unsupported catalog schema")
    entries = catalog["entries"]
    for key in ("id", "url"):
        if len({entry[key] for entry in entries}) != len(entries):
            raise ValueError(f"Duplicate catalog {key}")
    for entry in entries:
        if entry["category"] not in categories:
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


def render_analysis():
    path = ROOT / "analysis/results.json"
    if not path.exists():
        return []
    result = json.loads(path.read_text(encoding="utf-8"))
    scope = result["scope"]
    graph = result["knn_graph"]
    cross = result["cross_repository_graph"]
    skills = result["skills"]
    connected = [group for group in graph["communities"] if len(group) > 1]
    cluster_sizes = sorted((len(group["members"]) for group in result["clusters"]), reverse=True)
    silhouette = max(row["silhouette"] for row in result["clustering_trials"])
    lines = [
        "## Skill similarity analysis",
        "",
        f"The reproducible analysis snapshot covers {scope['verified_skills']} checksum-verified skill entry files from {scope['repositories']} repositories, out of {scope['catalog_entries']} catalog resources. It uses classical text statistics and randomized algorithms, with no model APIs or pretrained embeddings. Books, repository READMEs and linked references are outside this comparable-text sample. This compares skill instructions, not writing outputs, rendered interface designs or component quality.",
        "",
        f"A mutual five-nearest-neighbor graph finds {len(connected)} connected communities and {len(graph['isolates'])} unconnected skills at the chosen 0.15 similarity threshold. Median group agreement after randomly removing 20% of each skill's retained lines is {graph['perturbation_ari_median']:.2f} on adjusted Rand agreement (1 means identical partitions; 0 is chance-level agreement). These are exploratory wording groups, not schools of thought or effectiveness rankings.",
        "",
        f"Hard hierarchical clusters separate poorly: the largest silhouette score is {silhouette:.3f}, and the selected split has group sizes {', '.join(map(str, cluster_sizes))}. Eight non-negative matrix factorization topics instead expose overlapping vocabularies around prose editing, technical articles, marketing/email, fiction critique and video production. Topic weights are not probabilities.",
        "",
        "![Lexical neighborhood map](analysis/neighborhood-map.png)",
        "",
        "The map compresses many text dimensions into two. Follow graph edges and exact scores rather than reading every plotted distance literally. Numbers identify the skills in the index below.",
        "",
        f"The second map excludes same-repository candidates before choosing nearest neighbors: it has {sum(len(group)>1 for group in cross['communities'])} connected groups, {len(cross['isolates'])} unconnected skills, and median perturbation agreement of {cross['perturbation_ari_median']:.2f}. This helps separate a publisher's shared framing from resemblance across publishers. It does not make repositories independent; adaptations may still share an upstream source. Cross-repository neighbor lists and sensitivity to neighbor count and edge threshold are included in the full results.",
        "",
        "![Cross-repository neighborhood map](analysis/cross-repository-map.png)",
        "",
        "### Observed lexical overlap",
        "",
        "The largest pair scores in this snapshot are shown below. A score measures shared wording, not the share of rules that agree or a probability of copying. Negation and examples can make opposing instructions look similar.",
        "",
        "| Skill | Neighbor | Combined cosine | Shared five-word phrase Jaccard |",
        "| --- | --- | ---: | ---: |",
    ]
    for pair in result["top_pairs"][:5]:
        a, b = skills[pair["a"]], skills[pair["b"]]
        lines.append(f"| {a['repo']} | {b['repo']} | {pair['combined']:.3f} | {pair['phrase_jaccard']:.3f} |")
    lines += [
        "",
        "![Pairwise lexical similarity heatmap](analysis/similarity-heatmap.png)",
        "",
        "### Shared vocabulary and mixed topics",
        "",
        "The shared-vocabulary cloud counts each repository once per term, reducing the influence of publishers with several collected skills. Repositories can still share an upstream source. Frequent words and quoted bad examples are mentions, not endorsed writing principles.",
        "",
        "![Repository-balanced shared vocabulary](analysis/shared-vocabulary.png)",
        "",
        "![Eight topic word clouds](analysis/topic-wordclouds.png)",
        "",
        "![Per-skill topic mixtures](analysis/topic-mixtures.png)",
        "",
        "### Robustness and extractive distillation",
        "",
        "Word, character, latent-factor and exact-phrase methods reveal different kinds of resemblance. The correlations below compare all skill pairs; they are not independent observations or statistical significance tests.",
        "",
        "![Correlations between similarity methods](analysis/method-correlations.png)",
        "",
        f"An extractive experiment selects 20 paragraph locations to cover repeated, repository-balanced vocabulary while penalizing length. They cover {result['extractive_coverage'][-1]['vocabulary_coverage']:.1%} of that vocabulary weight. This is a compact set of passages to inspect, not a synthesized skill or a quality recommendation. Phrase-order permutation controls and source locators are retained in the results.",
        "",
        "![Grouping stability and extractive coverage](analysis/stability-and-coverage.png)",
        "",
        "[Methods and reproduction](docs/guides/skill-analysis.md) · [Full results](analysis/results.json) · [Skill index and nearest neighbors](analysis/skills.csv) · [All pair scores](analysis/pairs.csv)",
        "",
        "<details>",
        "<summary>Skill index for the figures</summary>",
        "",
        "| Index | Skill | Graph group |",
        "| ---: | --- | ---: |",
    ]
    for i, skill in enumerate(skills):
        lines.append(f"| {i+1} | [{skill['title']}]({skill['source_url']}) | {skill['graph_group']+1} |")
    return lines + ["", "</details>", ""]


def render_categories(entries, categories):
    lines = []
    for category in categories:
        lines += [f"## {category}", ""]
        members = sorted(
            (entry for entry in entries if entry["category"] == category),
            key=lambda entry: entry["title"].lower(),
        )
        for entry in members:
            lines.append(f"- [{entry['title']}]({entry['url']}) - {entry['description']}")
        lines.append("")
    return lines


def render_ui(entries):
    return "\n".join([
        "# UI design references",
        "",
        "Companion to [Awesome Anti-Slop](../README.md), whose main collection focuses on writing.",
        "",
        f"{len(entries)} resources for interface inspiration, components and design skills. Alphabetical; no rankings or recommendations.",
        "",
        "[catalog.json](catalog.json) records source URLs, pinned skill revisions, checksums, inspection scope and license metadata. Descriptions reflect inspected public pages or skill entries; components and generated designs were not independently evaluated. Linked designs, components and bundled references retain their own reuse terms.",
        "",
        *render_categories(entries, ["UI design"]),
        "## Contributing",
        "",
        "Add UI resources to `ui/catalog.json` and regenerate both documents with `python3 scripts/render.py` from the repository root. Keep source attribution and inspection limits. Run `mise run check` to validate both collections, generated documents and links.",
        "",
    ])


def render(entries):
    lines = [
        "# Awesome Anti-Slop",
        "",
        "Skills, prompts, tools and references for writing: anti-slop editing, copywriting, articles, email, newsletters, social posts and scripts.",
        "",
        "UI inspiration, component libraries and design skills are collected separately in the [UI design companion](ui/README.md).",
        "",
        f"{len(entries)} resources. Alphabetical within each category. No rankings or recommendations.",
        "",
        "The collection comes first. The next stage is an amalgamation of the collected methods, with attribution and conflicting rules kept visible. Sources remain separate here so that work can be traced back to their authors.",
        "",
        "[catalog.json](catalog.json) contains source URLs, pinned Git revisions, checksums, inspection dates and license metadata. Reading and course entries also record authors, access type and inspection scope. Descriptions reflect inspected entry files or public documentation; inclusion does not claim tested effectiveness.",
        "",
        "## Contents",
        "",
    ]
    for category in CATEGORIES:
        lines.append(f"- [{category}](#{category.lower().replace(' ', '-')})")
    if (ROOT / "analysis/results.json").exists():
        lines.append("- [Skill similarity analysis](#skill-similarity-analysis)")
    lines += ["- [Collection and provenance](#collection-and-provenance)", "- [Contributing](#contributing)", ""]
    lines += render_categories(entries, CATEGORIES)
    lines += render_analysis()
    lines += [
        "## Collection and provenance",
        "",
        "The main catalog includes individual writing skills, multi-skill repositories, prompts, linters, writing guides, books, blogs, newsletters, courses and research. Video entries distinguish script and prompt guidance from production/API workflows. Platform-published and community resources are identified in their descriptions; support for a platform does not imply that platform authored the resource. A repository containing many skills counts as one resource when collected at repository level. Separate skill entries identify their paths. This is an expanding collection, not an exhaustive inventory.",
        "",
        "Reading entries distinguish free resources, paid books and courses, and mixed-access publications. Free access is not permission to republish or adapt. A book description, course syllabus or archive index is recorded as such, not as a full review of the underlying material. Newsletter and columnist entries may supply examples for later style analysis; they are not automatically writing instruction. No paid material was purchased or unlocked to build this collection.",
        "",
        "Related projects can share rules, translations or source material. Their entries remain distinct. `related_sources` records relationships stated in inspected sources; it is not a complete genealogy. A GitHub fork flag alone would miss adaptations copied into separate repositories.",
        "",
        "GitHub sources have a pinned revision and a SHA-256 checksum of the retrieved entry file. A non-Git source has a retrieval date and checksum without a revision pin. These records identify what was retrieved; they do not certify a complete review of every referenced file or bundled skill.",
        "",
        "GitHub license fields come from repository metadata; other entries state their license basis separately. A missing value means no license was recorded, not that the material is free to reuse. File-specific terms and dependencies still need inspection before an amalgamation incorporates upstream text. This collection links to source material without republishing it.",
        "",
        "Discovery has included GitHub and web searches, [Awesome Humanizer Skills](https://github.com/zhuyansen/awesome-humanizer-skills) and the [AI Writing Skill Field Guide](https://github.com/Daguilar0123/ai-writing-skill-field-guide). Their rankings and assessments are not adopted here.",
        "",
        "## Contributing",
        "",
        "Open an issue with a source URL, or add a record to `catalog.json` in a pull request. Include the author, category, a neutral description, inspected source URL, revision where available, checksum, inspection date and license metadata. For an adaptation, record its stated sources. Do not add rankings, endorsements or performance claims without attribution.",
        "",
        "The main collection covers writing, editing, research for writing, voice, scripts, correspondence, content planning and published writing examples across languages. Books and courses may be included through public descriptions, with access and inspection scope stated. Interface inspiration, component libraries and design or redesign skills belong in the [UI design companion](ui/README.md) and its `ui/catalog.json`. General-purpose apps unrelated to either collection are outside scope.",
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
    outputs = (
        render(load_catalog()),
        render_ui(load_catalog(ROOT / "ui/catalog.json", ["UI design"])),
    )
    for name, output in zip(DOCUMENTS, outputs, strict=True):
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != output:
                parser.exit(1, f"{name} is stale; run python3 scripts/render.py\n")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(output, encoding="utf-8")
    if args.check:
        print("Both catalogs valid; generated READMEs match.")


if __name__ == "__main__":
    main()
