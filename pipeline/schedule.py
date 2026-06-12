"""Orchestration. v0: run with cron every 3 days. v1: Temporal workflow.

Constrain -> Validate -> Retry -> Checkpoint -> Supervise.
"""
import argparse, json, pathlib, uuid, datetime
from .config import CFG
from .interest_graph import InterestGraph
from . import writer, critic, publisher

def checkpoint(run_dir, name, payload):
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / name).write_text(payload if isinstance(payload, str)
                                else json.dumps(payload, indent=2))

def run_once():
    run_id = f"dv-{datetime.date.today()}-{uuid.uuid4().hex[:4]}"
    run_dir = pathlib.Path(CFG.runs_dir) / run_id

    graph = InterestGraph()
    graph.decay()
    topics = graph.top(5)
    checkpoint(run_dir, "interests.json", dict(topics))

    topic, _ = topics[0]
    brief = f"Write a Datavoid post about: {topic}. Angle: practitioner, hands-on."
    research = ""  # v1: web research tool call per topic
    checkpoint(run_dir, "brief.md", brief)

    notes = ""
    for loop in range(CFG.max_loops):
        draft = writer.write_draft(brief, research, notes)
        checkpoint(run_dir, f"draft_v{loop+1}.md", draft)
        verdict, notes = critic.review(draft)
        checkpoint(run_dir, f"critique_v{loop+1}.md", verdict + "\n" + notes)
        if verdict == "APPROVE":
            break

    title = draft.splitlines()[0].lstrip("# ").strip()
    publisher.publish(draft, title, run_id)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true")
    args = p.parse_args()
    if args.once:
        run_once()
