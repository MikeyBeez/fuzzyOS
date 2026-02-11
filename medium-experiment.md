# I Tested Whether Context Quality Beats Context Length. The Results Weren't Close.

## 43% accuracy with full context. 100% with curated context. Same model, same facts.

I recently published a paper arguing that context selection, not context length, is the dominant factor in language model reasoning quality. The paper proposes an operating system architecture for LLMs — a curator agent that manages what goes into the context window, the way an OS manages memory for a CPU. You can read it [here](https://github.com/MikeyBeez/fuzzyOS).

Three foundation models reviewed the architecture with full conversational context and agreed it was sound. But a design proposal is a design proposal. I wanted data.

So I tested it.

## The Setup

I built a 78-turn conversation — about 6,400 words — that looks like a real working session. A developer building a REST API for a bookstore inventory system. The conversation has everything a real conversation has:

- Topic shifts (API design → Docker debugging → Raspberry Pi weather station → back to the API)
- Corrections ("Actually, let's use PostgreSQL instead of MySQL")
- Dead ends ("Should I use Redis for caching?" ... "Never mind, that's premature optimization")
- Abandoned approaches (WebSockets explored then dropped in favor of polling)
- Verbose error outputs (full pytest tracebacks, Docker Compose errors)
- Off-topic tangents (Rust lifetime annotations, Box vs Rc vs Arc, whether Rust will replace Python for data science)

None of this was artificially stuffed. It's the kind of noise that accumulates naturally in any long conversation with an LLM. If you've ever worked with Claude, ChatGPT, or a local model on a multi-hour project, this is what your context window looks like.

I embedded 10 specific facts across the conversation. Things like: the PostgreSQL instance runs on port 5433, JWT tokens expire after 48 hours, the BME280 sensor uses I2C address 0x76, the default pagination size is 20 items.

Then I asked the model 10 questions — one per fact — under two conditions:

1. **Full context:** The entire 78-turn conversation as a flat sequential log, followed by the question. This is how every LLM interface works today.
2. **Curated context:** Only the relevant thread for each question — just the exchanges where that specific fact was discussed.

Same model. Same facts available. Same questions. The only difference is what context the model sees when it tries to answer.

The model was llama3.1 8B running locally through Ollama. Not a frontier model. An 8-billion parameter model on consumer hardware. Each question was run 3 times per condition at temperature 0.1 to minimize variance.

## The Results

| Question | Full Context | Curated Context |
|----------|-------------|----------------|
| Database system and port | 0/3 | 3/3 |
| Auth roles and permissions | 3/3 | 3/3 |
| Rate limit for search | 3/3 | 3/3 |
| Official project name | 3/3 | 3/3 |
| JWT token expiry | 0/3 | 3/3 |
| CSV duplicate handling | 1/3 | 3/3 |
| Gunicorn workers in Dockerfile | 3/3 | 3/3 |
| BME280 I2C address | 0/3 | 3/3 |
| Why Redis was skipped | 0/3 | 3/3 |
| Pagination page size | 0/3 | 3/3 |
| **Total** | **43.3%** | **100%** |

Full context: 43.3%. Curated context: 100%.

The delta isn't subtle. It's 56.7 percentage points on straightforward fact retrieval.

## What Went Wrong

The failures aren't random. They're systematic, and they're exactly the failure modes my paper predicts.

**The model picked the wrong version of a corrected fact.** When asked about the database port, the model said 5432 — the default PostgreSQL port, and the port discussed during a Docker Compose debugging session later in the conversation. The actual answer is 5433, stated earlier when the user specified their hosting provider's non-standard port. Both numbers are in the conversation. The model picked the wrong one. This is the contradiction problem: when the context window contains both a correct answer and a plausible alternative, the model sometimes chooses wrong.

**The model denied information existed.** When asked about the BME280 sensor's I2C address, the model responded: "We didn't discuss the BME280 sensor or I2C addresses in our conversation." This is flatly false. The BME280 was discussed across six turns — the sensor library, the I2C address (0x76), whether it measures wind speed, auto-starting the logging script, and connecting an OLED display on the same I2C bus. Six turns. The model couldn't find any of it. The noise made it invisible.

**The model hallucinated a plausible wrong answer.** When asked about the pagination page size, the model confidently said "10 per page." The actual answer, explicitly stated in the conversation, is 20. The model didn't say "I'm not sure." It invented a number that sounds reasonable for pagination and stated it as fact.

**The model claimed the user never asked.** When asked about JWT token expiry, the model said: "You didn't ask me to set an expiration time for the JWT tokens." The user explicitly said "tokens should expire after 48 hours." It's right there in the conversation. The model lost it in the noise.

Every single failure follows the same pattern: the relevant information is in the context window, but the model can't reliably attend to it because it's surrounded by thousands of words of irrelevant context. The window isn't full. The model isn't out of capacity. The signal-to-noise ratio is just too low.

## What This Means

The curated condition scored 100%. That means the model *can* answer every question correctly. It has the capability. The full context condition doesn't reveal a limitation of the model — it reveals a failure of information management.

This is a 6,400-word conversation. That's roughly 8,500 tokens. The model's context window is 128,000 tokens. We're using less than 7% of the available window, and the model is already failing nearly 60% of the time on basic fact retrieval.

Now extrapolate. What happens at 20,000 words? 50,000? What happens when the conversation includes not just topic shifts and corrections, but full web search results, tool call metadata, file contents, API responses, and hours of accumulated back-and-forth? The noise grows linearly. The model's ability to find what matters degrades.

The current solution from every major AI company is to make the window bigger. OpenAI, Google, and Anthropic are all racing toward million-token windows. But a bigger window full of noise is still full of noise. You don't fix a signal-to-noise problem by adding capacity. You fix it by managing what's in the window.

## The Architecture

My [paper](https://github.com/MikeyBeez/fuzzyOS) proposes exactly that: an operating system for language models that separates context management from reasoning.

A lightweight curator agent — something like Llama 3 running locally — continuously watches the conversation, organizes it into threads (not flat logs), tracks metadata and provenance, and assembles a curated input for each turn of the reasoning agent. The reasoning agent never sees the raw conversation. It sees what the curator decides it should see.

The experiment is a proof of concept for the simplest version of this. The "curator" was me, manually extracting the relevant thread for each question. A real implementation would automate this — thread detection, relevance scoring, manifest assembly — and learn from user corrections over time.

But the manual version already shows the magnitude of the effect. If hand-curated context takes you from 43% to 100%, even an imperfect automated curator that gets you to 80% or 90% would be a massive improvement over the status quo.

## Try It Yourself

The experiment is fully reproducible. You need Ollama with llama3.1 installed and about 15 minutes:

```bash
git clone https://github.com/MikeyBeez/fuzzyOS
cd fuzzyOS
python3 experiment/run_test.py
```

The conversation, questions, curated threads, and scoring logic are all in the `experiment/` directory. The conversation is realistic enough that you can read through it and see exactly where the noise accumulates.

Everything — the paper, the experiment, the data — is open source under CC-BY-4.0 with a Zenodo DOI ([10.5281/zenodo.18571717](https://doi.org/10.5281/zenodo.18571717)).

## The Bigger Point

Everyone in AI is chasing scale. Bigger models, bigger windows, bigger training runs. The assumption is that understanding comes from scale.

But understanding isn't a property of the model alone. Understanding emerges from the relationship between the model and its context. Get the context right and a modest model produces remarkable results. Get it wrong and the most powerful model in the world stumbles.

I gave an 8-billion parameter model the right context and it scored 100%. I gave it the wrong context — not adversarial, not corrupted, just naturally accumulated noise — and it scored 43%.

The model didn't change. The context did.

Context management isn't a feature. It's the foundation.

---

*The paper, experiment code, and discussion forum are at [github.com/MikeyBeez/fuzzyOS](https://github.com/MikeyBeez/fuzzyOS). The forum is open to humans and AI agents.*
