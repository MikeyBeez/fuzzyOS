#!/usr/bin/env python3
"""Post experiment results to GitHub Discussions."""

import subprocess
import json
import sys

RESULTS_LLAMAINDEX = """Following up on the [design paper](https://github.com/MikeyBeez/fuzzyOS) posted here earlier — we ran an empirical test of the central claim.

**Setup:** A 78-turn conversation (~6,400 words) with natural noise accumulation (topic shifts, corrections, abandoned approaches, off-topic tangents) fed to llama3.1 8B via Ollama. 10 fact-retrieval questions, tested under two conditions: full flat-log context vs curated thread-only context.

**Result: 43.3% accuracy (full context) vs 100% accuracy (curated context).**

The model hallucinated facts, denied information existed in the conversation, and picked up contradicted details from noise. Exactly the failure modes predicted by the paper.

Full results, methodology, and reproducible code: [github.com/MikeyBeez/fuzzyOS/discussions/2](https://github.com/MikeyBeez/fuzzyOS/discussions/2)

The takeaway for retrieval/context systems: a well-curated short context dramatically outperforms a noisy long context, even when the long context is well within the model's window. Context selection dominates context length."""

RESULTS_AUTOGEN = RESULTS_LLAMAINDEX.replace(
    "The takeaway for retrieval/context systems",
    "The takeaway for agent memory systems"
)

RESULTS_SK = RESULTS_LLAMAINDEX.replace(
    "The takeaway for retrieval/context systems",
    "The takeaway for kernel-level orchestration"
)

TITLE = "Experiment: Curated context (100%) vs flat log (43%) on llama3.1 8B"

POSTS = [
    ("R_kgDOIWuq5w", "DIC_kwDOIWuq584CaCBH", "LlamaIndex", RESULTS_LLAMAINDEX),
    ("R_kgDOKInPBw", "DIC_kwDOKInPB84CZqqP", "AutoGen", RESULTS_AUTOGEN),
    ("R_kgDOJDJ_YQ", "DIC_kwDOJDJ_Yc4CUlKT", "Semantic Kernel", RESULTS_SK),
]

for repo_id, cat_id, name, body in POSTS:
    query = """
    mutation($repoId: ID!, $catId: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {
        repositoryId: $repoId,
        categoryId: $catId,
        title: $title,
        body: $body
      }) {
        discussion { url }
      }
    }
    """
    result = subprocess.run(
        ["gh", "api", "graphql",
         "-f", f"query={query}",
         "-f", f"repoId={repo_id}",
         "-f", f"catId={cat_id}",
         "-f", f"title={TITLE}",
         "-f", f"body={body}"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        url = data["data"]["createDiscussion"]["discussion"]["url"]
        print(f"{name}: {url}")
    else:
        print(f"{name}: FAILED - {result.stderr}", file=sys.stderr)
