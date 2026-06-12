"""Carder agent: turns an approved essay into an ADHD-friendly card deck.

Runs AFTER critic approval, BEFORE publish. Output: content/decks/<slug>.json
Each deck: 5-7 cards, one idea per card, <= 40 words each, ordered as
hook -> core -> evidence -> visual/code -> takeaway -> cta.
"""
import anthropic, json, pathlib
from .config import CFG

CARD_SCHEMA = {
    "drop_id": "str", "title": "str", "topic": "str",
    "fresh_until": "ISO8601 (publish + 72h)",
    "cards": [{"kind": "hook|core|evidence|code|takeaway|cta",
               "title": "str <= 8 words", "body": "str <= 40 words",
               "code": "optional str", "stat": "optional {value, label}",
               "seconds": "int, honest read time"}],
}

def make_deck(post_markdown: str) -> dict:
    client = anthropic.Anthropic(api_key=CFG.api_key)
    system = pathlib.Path("prompts/carder.md").read_text()
    msg = client.messages.create(
        model=CFG.writer_model, max_tokens=2000, system=system,
        messages=[{"role": "user", "content": post_markdown}])
    text = msg.content[0].text.replace("```json", "").replace("```", "").strip()
    deck = json.loads(text)
    assert 5 <= len(deck["cards"]) <= 7, "deck must be 5-7 cards"
    for c in deck["cards"]:
        assert len(c["body"].split()) <= 40, "card body over 40 words"
    return deck

def save_deck(deck: dict, slug: str):
    out = pathlib.Path("content/decks") / f"{slug}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(deck, indent=2))
    return out
