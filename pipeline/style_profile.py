"""Learn Rui's voice from Datavoid (rpmachado.wordpress.com).

Bootstraps prompts/style_profile.yaml from the blog RSS + archive,
then refreshes periodically so new posts feed back into the profile.
"""
import feedparser, yaml, pathlib, argparse

FEED = "https://rpmachado.wordpress.com/feed/"
OUT = pathlib.Path("prompts/style_profile.yaml")

def fetch_corpus():
    feed = feedparser.parse(FEED)
    return [{"title": e.title, "html": e.get("content", [{}])[0].get("value", "")}
            for e in feed.entries]

def bootstrap():
    """v0 ships a hand-curated profile (see prompts/style_profile.yaml).
    v1: send the corpus to the critic model and ask it to update the
    profile fields, keeping the anti_patterns list locked."""
    corpus = fetch_corpus()
    print(f"Fetched {len(corpus)} posts. Profile at {OUT} (curated, LLM refresh TODO).")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--bootstrap", action="store_true")
    args = p.parse_args()
    if args.bootstrap:
        bootstrap()
