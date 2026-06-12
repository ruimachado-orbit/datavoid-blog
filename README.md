# Datavoid v2 — Agent-Driven Blog

An autonomous publication. An agent pipeline digests Rui's Hermes conversations, maintains an interest graph, and publishes a new essay on technology and AI every 3 days, written in Rui's voice (learned from rpmachado.wordpress.com) and supervised by Rui.

Tagline kept from v1: `data > code > enlightening`

---

## 1. System overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                            DATAVOID PIPELINE                           │
│                                                                        │
│  SOURCES                 KNOWLEDGE                EDITORIAL            │
│                                                                        │
│  Hermes convo   ───►  Interest Graph  ───►  Topic Selector             │
│  exports (JSONL)      (topics, weights,        │                       │
│                        recency decay)          ▼                       │
│  Datavoid corpus ──►  Style Profile   ───►  Writer Agent ──► Critic    │
│  (WordPress RSS)      (voice, structure,       │             Agent     │
│                        lexicon, anti-rules)    │ retry loop    │       │
│  Web research   ──────────────────────────────►│              ▼        │
│  (per-topic, fresh sources)                    │         Approval Gate │
│                                                ▼          (optional)   │
│                                          content/posts/*.md            │
│                                                │                       │
│                                                ▼                       │
│                                   git commit ──► CI ──► static site    │
└────────────────────────────────────────────────────────────────────────┘
```

Reliability model follows the five principles: **Constrain, Validate, Retry, Checkpoint, Supervise.**

- **Constrain**: writer receives a locked style profile, a topic brief, and a strict output schema (frontmatter + markdown).
- **Validate**: critic agent scores the draft against the style profile and a fact checklist; schema validation on frontmatter.
- **Retry**: up to 3 writer↔critic loops; deterministic backoff on LLM/API failures.
- **Checkpoint**: every stage persists its artifact (interest snapshot, topic brief, draft vN, critique vN) to `runs/<run_id>/`.
- **Supervise**: optional human approval gate (email/Slack with diff link) before the publish commit; full provenance stored in the post frontmatter and exposed in the UI.

## 2. Components

| Module | Role |
|---|---|
| `pipeline/ingest_hermes.py` | Parses Hermes conversation exports (JSONL/Markdown), chunks, embeds, extracts candidate topics |
| `pipeline/interest_graph.py` | Maintains weighted topic graph with recency decay; merges CV-derived seed interests |
| `pipeline/style_profile.py` | One-off + periodic job: crawls Datavoid RSS, derives a style profile (voice, structure, lexicon, anti-patterns) into `prompts/style_profile.yaml` |
| `pipeline/writer.py` | Generates the draft from topic brief + style profile + fresh web research |
| `pipeline/critic.py` | Scores draft (style fidelity, factuality, structure); emits revision notes or APPROVE |
| `pipeline/publisher.py` | Writes markdown to `content/posts/`, commits, triggers CI |
| `pipeline/schedule.py` | Temporal workflow: cron `every 3 days`, orchestrates the stages with retries and checkpoints |
| `site/` | Static frontend (design in `site/index.html`); deployable to Vercel/Cloudflare Pages |

## 3. Data model

**Interest graph node**
```json
{"topic": "moe-inference", "weight": 0.87, "last_seen": "2026-06-10",
 "sources": ["hermes:conv_2391", "cv:deep-learning"], "decay": 0.97}
```

**Post frontmatter (provenance is first-class)**
```yaml
title: "Streaming experts: MoE inference under 16GB"
date: 2026-06-12
run_id: dv-2026-06-12-a3f1
interests: [moe-inference, llama-cpp, edge-ai]
pipeline: {writer: claude-sonnet-4-6, critic: claude-sonnet-4-6, loops: 2}
supervised: true
```

## 4. Seed interests (from CV + recent work)

Agentic AI and orchestration, LLM inference optimization (MoE, edge), data engineering and analytics engineering, AI governance and "own, not rent" infrastructure, engineering management, deep learning for vision (legacy), SQL/dbt.

## 5. Scaling path

- **Now (single node)**: cron + SQLite + files in git. Zero infra cost.
- **Next**: Temporal Cloud for orchestration, Qdrant for embeddings, Postgres for the interest graph.
- **Later**: multi-publication fan-out (LinkedIn carousel derivative, newsletter digest) as extra publisher targets on the same run artifact.

## 6. Run it

```bash
cp .env.example .env          # add ANTHROPIC_API_KEY
pip install -r requirements.txt
python -m pipeline.style_profile --bootstrap   # learn voice from Datavoid
python -m pipeline.ingest_hermes data/hermes/  # load conversations
python -m pipeline.schedule --once             # produce one post now
```

---

## 7. v3: Drops, decks and attention design

The publication model evolved from "posts" to **drops** with a dual lane per essay:

- **Fast lane (deck)**: 5-7 visual cards generated by the `carder` agent. One idea per card, <= 40 words, honest per-card seconds. Swipe-through with progress dots. Total under 3 minutes.
- **Deep lane (essay)**: the full markdown post, unchanged.

Pipeline gains one stage: `writer -> critic -> carder -> publish`. The carder validates its own schema (5-7 cards, 40-word cap) before publish.

### Attention contract (ADHD design rules, encoded in the UI)
1. One idea per visual unit. Cards never scroll internally.
2. Progress is always visible: deck dots, streak counter, countdown.
3. Honest time labels on everything (45s cards, 7 min essays).
4. Topic color coding (4 fixed hues) so recognition beats reading.
5. The fast lane is complete on its own. Depth is a choice, not homework.

### FOMO mechanics (kept honest)
- Each drop is **fresh for 72h** (until the next synthesis). The countdown is real: it is the pipeline cron.
- After 72h the drop moves to **The Vault** (archive), still readable but visually receded. Nothing is ever deleted: scarcity of freshness, not of access.
- **Reader streak**: consecutive drops opened. Stored client-side only (in-memory in preview; swap in persistent storage on production hosting, marked in code).
- **Missed-drops shelf**: "you missed 2 drops" with 1-line recaps, clearing the anxiety instead of farming it.
