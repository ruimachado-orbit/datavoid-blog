"""Writer agent: topic brief + style profile + research -> markdown draft."""
import openai, yaml, pathlib
from .config import CFG

def load_prompt(name):
    return pathlib.Path(f"prompts/{name}").read_text()

def write_draft(topic_brief: str, research: str, revision_notes: str = "") -> str:
    client = openai.OpenAI(api_key=CFG.api_key)
    style = yaml.safe_load(pathlib.Path("prompts/style_profile.yaml").read_text())
    system = load_prompt("writer.md").format(style=yaml.dump(style))
    user = f"TOPIC BRIEF:\n{topic_brief}\n\nRESEARCH:\n{research}"
    if revision_notes:
        user += f"\n\nREVISION NOTES (address all):\n{revision_notes}"
    response = client.chat.completions.create(
        model=CFG.writer_model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=4000)
    return response.choices[0].message.content
