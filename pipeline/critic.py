"""Critic agent: validates draft against style profile and structure rules.

Returns ("APPROVE", "") or ("REVISE", notes).
"""
import anthropic, pathlib
from .config import CFG

def review(draft: str):
    client = anthropic.Anthropic(api_key=CFG.api_key)
    system = pathlib.Path("prompts/critic.md").read_text()
    msg = client.messages.create(
        model=CFG.critic_model, max_tokens=1500,
        system=system, messages=[{"role": "user", "content": draft}])
    text = msg.content[0].text
    if text.strip().startswith("APPROVE"):
        return "APPROVE", ""
    return "REVISE", text
