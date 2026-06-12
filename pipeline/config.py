import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    api_key: str = os.getenv("ANTHROPIC_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    hermes_dir: str = os.getenv("HERMES_EXPORT_DIR", "data/hermes")
    cycle_days: int = int(os.getenv("CYCLE_DAYS", "3"))
    approval_gate: bool = os.getenv("APPROVAL_GATE", "true") == "true"
    writer_model: str = "gpt-4o"
    critic_model: str = "gpt-4o"
    max_loops: int = 3
    runs_dir: str = "runs"
    posts_dir: str = "content/posts"

CFG = Config()
