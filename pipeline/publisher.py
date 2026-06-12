"""Writes the approved post and commits it. CI deploys the static site."""
import pathlib, subprocess, datetime, re
from .config import CFG

def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

def publish(markdown: str, title: str, run_id: str, dry_run: bool = False):
    date = datetime.date.today().isoformat()
    path = pathlib.Path(CFG.posts_dir) / f"{date}-{slugify(title)}.md"
    path.write_text(markdown)
    if dry_run or CFG.approval_gate:
        print(f"Draft staged at {path}. Awaiting approval.")
        return path
    subprocess.run(["git", "add", str(path)], check=True)
    subprocess.run(["git", "commit", "-m", f"post: {title} ({run_id})"], check=True)
    subprocess.run(["git", "push"], check=True)
    return path
