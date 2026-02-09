# Understanding Is Getting the Context Right

**An Operating System for Language Models**

Michael Bonsignore, 2026

## Abstract

Current language model systems manage context by packing entire conversation histories sequentially into the context window, leading to progressive pollution that degrades reasoning quality. This paper argues that context selection, not context length, is the dominant factor in reasoning performance, and proposes a two-agent architecture that separates context management from reasoning. A lightweight curator agent continuously evaluates conversation history — organized as linked threads rather than flat logs — and assembles a curated input for each turn of the reasoning agent using two manifests: a compact topic index providing scope awareness, and an active context payload containing only relevant threads. The system includes provenance-aware metadata, exponential decay with user-overridable current theory marking, a persistent global repository that accumulates into an emergent knowledge graph, and a user interface that exposes context as a manipulable first-class object whose corrections serve as training signal for the curator. Combined with a protocol layer governing reasoning behavior, the architecture constitutes a fuzzy operating system for language models — one that learns and improves through use without retraining any weights.

## Reading the Paper

The paper is available as:
- [`paper.md`](paper.md) — Markdown source
- [`paper.pdf`](paper.pdf) — Formatted PDF

## Citation

If you reference this work, see [`CITATION.cff`](CITATION.cff) or use:

```bibtex
@article{bonsignore2026context,
  title={Understanding Is Getting the Context Right: An Operating System for Language Models},
  author={Bonsignore, Michael},
  year={2026},
  url={https://github.com/MikeyBeez/fuzzyOS}
}
```

## License

This work is licensed under [CC-BY-4.0](LICENSE).
