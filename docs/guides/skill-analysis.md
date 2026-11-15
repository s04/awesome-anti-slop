# Reproduce the skill similarity analysis

Run from the repository root:

```sh
mise run analyze
mise run check
```

`analyze` runs the dependency-locked Python script with `uv`, then regenerates the README. It requires network access for uncached sources and Python dependencies. Upstream source instructions are data and are never executed. It uses no language model, embedding service, model weights or paid API. Scientific packages are pinned in the script and its adjacent lock file.

## Corpus and source integrity

`catalog.json` is the writing inventory. The UI companion uses `ui/catalog.json` and does not enter this analysis. Only entries with `kind: skill` and a pinned GitHub source in the writing inventory are eligible. A book description, repository README and complete skill are not interchangeable documents. The analysis does not recursively read referenced guides, bundled examples or every skill inside repository-level entries. This limits conclusions about an entire skill bundle.

Sources are fetched at their recorded revision and verified against the catalog SHA-256 before analysis. The local `.cache/skill-analysis/` directory is ignored by Git. Failing sources are excluded with their errors recorded in `analysis/results.json`; never interpret missing sources as zero-similarity skills. Generated files contain measurements, vocabulary and source locators rather than copies of the full upstream texts.

The cleaning pass removes YAML frontmatter, fenced code, URLs and Markdown decoration. It retains prose examples, including examples labeled bad. Negation words remain. These choices prevent installation and configuration syntax from dominating the comparison, but can discard useful fenced writing examples. Tokenization is Unicode-aware but does not segment Chinese or other unspaced languages; multilingual similarities should be treated as exploratory.

## Similarity views

- Word similarity uses sublinear term-frequency/inverse-document-frequency (TF-IDF) unigrams and bigrams. Words shared across many documents receive less weight. Generic skill-framework terms and English stopwords are removed; `no`, `not`, `never` and `without` are retained.
- Character similarity uses TF-IDF of three-to-five-character sequences within word boundaries. It catches inflections and formatting variations, but shared language and terminology can inflate it.
- The combined exploratory score is 70% word cosine plus 30% character cosine. This weighting is a modeling choice, not a learned or calibrated quality metric. Both component scores remain available.
- Latent semantic analysis reduces word TF-IDF to 24 factors with seeded randomized singular value decomposition. These are corpus-derived factors, not pretrained embeddings. Its similarities are a separate diagnostic and do not drive the primary graph.
- Five-word-shingle Jaccard measures literal phrase overlap. Shingles never cross retained line boundaries. Phrase resemblance does not identify the original author or prove copying.
- A raw-text TF-IDF control exposes sensitivity to frontmatter, code and boilerplate. It has its own fitted vocabulary; differences are a preprocessing sensitivity check, not a causal decomposition.

The full pair matrices and all pair scores are exported. The five nearest neighbors per skill include component scores, phrase overlap, 5th/95th perturbation percentiles, and the share of perturbations in which that neighbor remains among the first five. This retention is not a probability that the skills are equivalent.

## Groups, topics and stochastic checks

The graph connects skills only when each is among the other's five nearest neighbors and their combined similarity is at least 0.15. Louvain communities use the resulting weighted graph. Isolated skills have no qualifying mutual edges, which does not establish novelty or quality. Louvain is repeated with 20 seeds; the exported agreement shows sensitivity to random initialization. Threshold 0.15 and neighbor count five are exploratory choices, not optimized truths. A second graph excludes same-repository candidates before choosing neighbors; it is also perturbed. The results include cross-repository graph sensitivity for neighbor counts 3, 5 and 8 and thresholds 0.10, 0.15 and 0.20. These controls expose publisher effects and parameter dependence; repositories can still have shared upstream authors.

For a contrasting hard partition, average-linkage hierarchical clustering is tested at 2 through 12 groups and compared by silhouette score. A high relative score does not imply useful separation: inspect the absolute score and group sizes. A separate latent-space k-means control is repeated across 20 seeds. Adjusted Rand agreement compares partitions with chance correction: one means identical partitions, approximately zero means chance-level agreement, and negative values are possible. A stable but uninformative giant group is still uninformative.

Eight-topic non-negative matrix factorization (NMF) lets a document contain multiple vocabularies. Topic names are their largest weighted words, without generated interpretations. Normalizing a document's NMF weights to sum to one does not make them probabilities. Eight is an exploratory resolution, not a selected true number of themes.

Sixty seeded perturbations retain a random 80% of each skill's prose lines without replacement, preserving order. The fitted vocabulary and inverse-document-frequency weights remain fixed to isolate sensitivity to missing passages. Neighbor retention and group agreement describe these particular perturbations. Their percentiles are not population confidence intervals and do not establish statistical significance.

For the ten pairs with the largest observed phrase overlap, 100 token-order permutations preserve a document's vocabulary while destroying its order. The output compares observed overlap with the shuffled 95th percentile. Because the pairs were selected after observing them, this is an exploratory sequence control; no hypothesis-test claim is made. Word/character/latent/phrase score correlations use all unordered skill pairs, whose shared documents make them dependent observations.

## Distillation experiments

The repository-balanced vocabulary cloud gives each repository one vote per term. It counts mentions, including prohibitions, examples and tool names. Repositories are not guaranteed independent: adaptations may share an upstream source. Neither term frequency nor topic membership establishes agreement about advice.

The extractive coverage experiment considers retained prose lines between 12 and 160 words. It weights vocabulary by mean TF-IDF within each repository, then averages those repository profiles, and restricts the target to terms occurring in at least three repositories. Each step chooses the passage giving the greatest uncovered target weight per word-count raised to 0.65. The exponent and 20-passage budget are declared choices. Full text is not exported: each choice records its source, retained-line number, word count and text checksum for local recovery.

This provides a reproducible set of passages to inspect before synthesis. It does not resolve contradictions, distinguish a rejected example from a recommendation, estimate writing quality or measure whether advice helps a model. Read the source context before turning a lexical theme into a rule.

The neighbor graph also records unweighted betweenness centrality: how often a skill lies on shortest graph paths. This can suggest bridges between vocabularies for inspection, but it is not a writing-quality or novelty score. The two-dimensional map uses metric multidimensional scaling (MDS); its stress and local-neighborhood trustworthiness are recorded because projected distances distort the full matrix.

## Outputs and validation

`analysis/results.json` records corpus eligibility, source hashes, failures, random seed, methods, full matrices, graph edges and groups, topic weights, stability, shared phrases and extraction locators. `analysis/skills.csv` supplies figure indices and nearest neighbors; `analysis/pairs.csv` supplies every unordered pair. The PNGs are standalone scientific figures, and the README embeds the report.

The catalog checksum identifies the inventory used by a snapshot. Later collection additions do not retroactively enter that snapshot; rerun the analysis to refresh it. Rendering the README does not itself recompute results.

The normal check task runs extraction regression tests, catalog and README validation, whitespace and link checks. After changing the analysis implementation, run `mise run analyze` and inspect the generated figures before committing. The locked execution should produce identical numeric results and figure hashes in the same environment.
