#!/usr/bin/env python3
"""
Context Curation Experiment for fuzzyOS

Tests the paper's central claim: curated context outperforms naturally
accumulated flat-log context for fact retrieval in multi-turn conversations.

Two conditions:
  1. Full context — entire conversation as a flat sequential log
  2. Curated context — only the relevant thread for each question

Model: llama3.1 via Ollama (local)
"""

import json
import time
import requests
from pathlib import Path

ROOT = Path(__file__).parent
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:latest"
RUNS = 3
TEMPERATURE = 0.1


def load_data():
    conversation = json.loads((ROOT / "conversation.json").read_text())
    questions = json.loads((ROOT / "questions.json").read_text())
    threads = json.loads((ROOT / "threads.json").read_text())
    return conversation, questions, threads


def query_model(messages, question):
    """Send conversation context + question to the model."""
    prompt_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
    prompt_messages.append({
        "role": "user",
        "content": f"Based on our conversation above, answer this question concisely: {question}"
    })

    resp = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": prompt_messages,
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": 150
        }
    }, timeout=120)
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def score_answer(answer, keywords):
    """Check if answer contains expected keywords (case-insensitive)."""
    answer_lower = answer.lower()
    return all(kw.lower() in answer_lower for kw in keywords)


def run_experiment():
    conversation, questions, threads = load_data()

    print("=" * 70)
    print("fuzzyOS Context Curation Experiment")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Conversation turns: {len(conversation)}")
    print(f"Questions: {len(questions)}")
    print(f"Runs per condition: {RUNS}")
    print(f"Temperature: {TEMPERATURE}")
    print()

    # Count tokens roughly (words as proxy)
    full_words = sum(len(m["content"].split()) for m in conversation)
    print(f"Full context size: ~{full_words} words")
    print()

    results = {"full": {}, "curated": {}}

    for q in questions:
        qid = q["id"]
        results["full"][qid] = []
        results["curated"][qid] = []

        thread_messages = threads[q["thread"]]
        curated_words = sum(len(m["content"].split()) for m in thread_messages)

        print(f"Q{qid}: {q['question']}")
        print(f"  Expected: {q['expected']}")
        print(f"  Thread: {q['thread']} (~{curated_words} words vs ~{full_words} full)")

        # --- Full context ---
        for run in range(RUNS):
            try:
                answer = query_model(conversation, q["question"])
                correct = score_answer(answer, q["keywords"])
                results["full"][qid].append(correct)
                mark = "Y" if correct else "N"
                print(f"  Full    run {run+1}: [{mark}] {answer[:80]}...")
            except Exception as e:
                print(f"  Full    run {run+1}: ERROR - {e}")
                results["full"][qid].append(False)

        # --- Curated context ---
        for run in range(RUNS):
            try:
                answer = query_model(thread_messages, q["question"])
                correct = score_answer(answer, q["keywords"])
                results["curated"][qid].append(correct)
                mark = "Y" if correct else "N"
                print(f"  Curated run {run+1}: [{mark}] {answer[:80]}...")
            except Exception as e:
                print(f"  Curated run {run+1}: ERROR - {e}")
                results["curated"][qid].append(False)

        print()

    # --- Summary ---
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"{'Q#':<4} {'Question':<55} {'Full':>8} {'Curated':>8}")
    print("-" * 70)

    full_total = 0
    curated_total = 0
    total_runs = 0

    for q in questions:
        qid = q["id"]
        full_correct = sum(results["full"][qid])
        curated_correct = sum(results["curated"][qid])
        full_total += full_correct
        curated_total += curated_correct
        total_runs += RUNS

        question_short = q["question"][:53]
        print(f"Q{qid:<3} {question_short:<55} {full_correct}/{RUNS}      {curated_correct}/{RUNS}")

    print("-" * 70)
    full_pct = (full_total / total_runs) * 100
    curated_pct = (curated_total / total_runs) * 100
    delta = curated_pct - full_pct
    print(f"{'TOTAL':<60} {full_pct:>5.1f}%   {curated_pct:>5.1f}%")
    print(f"{'DELTA':<60} {'+' if delta >= 0 else ''}{delta:.1f}%")
    print()

    if delta > 0:
        print(f"Curated context outperformed full context by {delta:.1f} percentage points.")
    elif delta == 0:
        print("No difference between conditions.")
    else:
        print(f"Full context outperformed curated context by {-delta:.1f} percentage points.")

    # Save raw results
    output = {
        "model": MODEL,
        "runs": RUNS,
        "temperature": TEMPERATURE,
        "conversation_turns": len(conversation),
        "full_context_words": full_words,
        "results": {
            "full": {str(k): v for k, v in results["full"].items()},
            "curated": {str(k): v for k, v in results["curated"].items()}
        },
        "accuracy": {
            "full": full_pct,
            "curated": curated_pct,
            "delta": delta
        }
    }
    out_path = ROOT / "results.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nRaw results saved to {out_path}")


if __name__ == "__main__":
    run_experiment()
