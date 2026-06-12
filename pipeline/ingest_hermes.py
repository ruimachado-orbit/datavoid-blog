"""Ingest Hermes conversation exports and extract candidate interests.

Expected input: JSONL files, one message per line:
  {"conversation_id": "...", "role": "user|assistant", "text": "...", "ts": "ISO8601"}
"""
import json, pathlib, collections
from .config import CFG

STOPWORDS = set()  # extend as needed

def load_conversations(directory: str):
    for path in pathlib.Path(directory).glob("*.jsonl"):
        with open(path) as f:
            for line in f:
                yield json.loads(line)

def extract_candidate_topics(messages) -> dict:
    """v0: naive keyphrase counting. v1: replace with LLM topic extraction
    over conversation windows (see prompts/topic_extraction.md)."""
    counts = collections.Counter()
    for m in messages:
        if m.get("role") != "user":
            continue
        for token in m.get("text", "").lower().split():
            if len(token) > 4 and token not in STOPWORDS:
                counts[token] += 1
    return dict(counts.most_common(200))

if __name__ == "__main__":
    msgs = list(load_conversations(CFG.hermes_dir))
    print(json.dumps(extract_candidate_topics(msgs), indent=2))
