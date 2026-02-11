# Understanding Is Getting the Context Right

**An Operating System for Language Models**

Michael Bonsignore, 2026

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18571717.svg)](https://doi.org/10.5281/zenodo.18571717)

## Abstract

Current language model systems manage context by packing entire conversation histories sequentially into the context window, leading to progressive pollution that degrades reasoning quality. This paper argues that context selection, not context length, is the dominant factor in reasoning performance, and proposes a two-agent architecture that separates context management from reasoning. A lightweight curator agent continuously evaluates conversation history — organized as linked threads rather than flat logs — and assembles a curated input for each turn of the reasoning agent using two manifests: a compact topic index providing scope awareness, and an active context payload containing only relevant threads. The system includes provenance-aware metadata, exponential decay with user-overridable current theory marking, a persistent global repository that accumulates into an emergent knowledge graph, and a user interface that exposes context as a manipulable first-class object whose corrections serve as training signal for the curator. Combined with a protocol layer governing reasoning behavior, the architecture constitutes a fuzzy operating system for language models — one that learns and improves through use without retraining any weights.

## Reading the Paper

The paper is available as:
- [`paper.md`](paper.md) — Markdown source
- [`paper.pdf`](paper.pdf) — Formatted PDF

## Experiment

An empirical test of the paper's central claim. A 78-turn conversation (~6,400 words) with natural noise accumulation was used to test fact retrieval under two conditions:

| Condition | Accuracy |
|-----------|----------|
| Full flat-log context | 43.3% |
| Curated thread context | 100% |

The model (llama3.1 8B) hallucinated facts, denied information existed, and picked up contradicted details from noise — exactly the failure modes the paper predicts. Same model, same facts, different context quality.

Reproduce with:
```bash
# Requires ollama with llama3.1 running locally
python3 experiment/run_test.py
```

See [`experiment/`](experiment/) for full methodology and data.

## Discussion

Join the conversation — humans and AI agents welcome: [**Discussions**](https://github.com/MikeyBeez/fuzzyOS/discussions)

## Citation

If you reference this work, see [`CITATION.cff`](CITATION.cff) or use:

```bibtex
@article{bonsignore2026context,
  title={Understanding Is Getting the Context Right: An Operating System for Language Models},
  author={Bonsignore, Michael},
  year={2026},
  doi={10.5281/zenodo.18571717},
  url={https://doi.org/10.5281/zenodo.18571717}
}
```

## License

This work is licensed under [CC-BY-4.0](LICENSE).
