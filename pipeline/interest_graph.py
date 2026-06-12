"""Weighted interest graph with recency decay. SQLite-backed (v0)."""
import sqlite3, time, math, json

SEED_INTERESTS = [
    # from CV and current work
    "agentic ai", "llm inference optimization", "moe models", "edge ai",
    "data engineering", "analytics engineering", "sql and dbt",
    "ai governance", "own-not-rent ai infrastructure",
    "engineering management", "computer vision",
]

class InterestGraph:
    def __init__(self, db="interests.db"):
        self.conn = sqlite3.connect(db)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS interests(
            topic TEXT PRIMARY KEY, weight REAL, last_seen REAL, sources TEXT)""")
        for t in SEED_INTERESTS:
            self.conn.execute(
                "INSERT OR IGNORE INTO interests VALUES(?,?,?,?)",
                (t, 0.5, time.time(), json.dumps(["cv"])))
        self.conn.commit()

    def reinforce(self, topic, amount, source):
        row = self.conn.execute(
            "SELECT weight, sources FROM interests WHERE topic=?", (topic,)).fetchone()
        if row:
            weight = min(1.0, row[0] + amount)
            sources = list(set(json.loads(row[1]) + [source]))
            self.conn.execute(
                "UPDATE interests SET weight=?, last_seen=?, sources=? WHERE topic=?",
                (weight, time.time(), json.dumps(sources), topic))
        else:
            self.conn.execute("INSERT INTO interests VALUES(?,?,?,?)",
                              (topic, amount, time.time(), json.dumps([source])))
        self.conn.commit()

    def decay(self, half_life_days=30.0):
        now = time.time()
        for topic, weight, last_seen in self.conn.execute(
                "SELECT topic, weight, last_seen FROM interests").fetchall():
            age_days = (now - last_seen) / 86400
            decayed = weight * math.pow(0.5, age_days / half_life_days)
            self.conn.execute("UPDATE interests SET weight=? WHERE topic=?",
                              (decayed, topic))
        self.conn.commit()

    def top(self, n=5):
        return self.conn.execute(
            "SELECT topic, weight FROM interests ORDER BY weight DESC LIMIT ?",
            (n,)).fetchall()
