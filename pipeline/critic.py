"""Critic agent: validates draft against style profile and structure rules.

Returns ("APPROVE", "") or ("REVISE", notes).
"""
import openai, yaml, pathlib
from .config import CFG

def review(draft: str):
    client = openai.OpenAI(api_key=CFG.api_key, base_url=CFG.base_url)
    system = pathlib.Path("prompts/critic.md").read_text()
    response = client.chat.completions.create(
        model=CFG.critic_model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": draft}],
        max_tokens=1500)
    text = response.choices[0].message.content
    if text.strip().startswith("APPROVE"):
        return "APPROVE", ""
    return "REVISE", text
