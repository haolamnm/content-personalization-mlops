---
name: teach
description: Teach the user a new skill or concept over multiple sessions, with state kept under `.notes/teach/<topic>/`. Includes ELI5 visual explainers for foundational concepts.
argument-hint: "What would you like to learn about?"
---

The user has asked you to teach them something. This is a stateful request — they intend to learn the topic over multiple sessions.

## Teaching Workspace

Each topic gets its own teaching workspace at `.notes/teach/<topic>/` (local-only, like the rest of `.notes/` — never commit or stage it). The state of their learning lives in these files:

- `MISSION.md`: A document capturing the _reason_ the user is interested in the topic. This grounds all teaching. Use the format in [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `./reference/*.html`: A directory of reference materials. These are the compressed learnings from lessons — cheat sheets, syntax, glossaries. They should be beautiful documents which print out well, designed for quick reference.
- `RESOURCES.md`: A list of resources which ground teaching in contextual knowledge. Use the format in [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `./learning-records/*.md`: Learning records capturing what the user has learned — the teaching equivalent of ADRs. They capture non-obvious lessons and key insights that steer future sessions and define the zone of proximal development. Titled `0001-<dash-case-name>.md`, incrementing each time. Format in [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `GLOSSARY.md`: Canonical language for the topic, per [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md). All explainers, exercises, and records adhere to its terminology.
- `./lessons/*.html`: A directory of lessons. A **lesson** is a single, self-contained HTML output that teaches one tightly-scoped thing tied to the mission. This is the primary unit of teaching.
- `./assets/*`: Reusable **components** shared across lessons (stylesheets, quiz widgets, diagram helpers). See [Assets](#assets).
- `NOTES.md`: Scratchpad for teaching preferences and working notes.

When the topic relates to this workspace's MLOps build (e.g. Helm for deploying the platform), tie lessons back to the relevant ADRs, CONTEXT-MAP vocabulary, and roadmap phase — the mission section below covers this.

## Philosophy

To learn at a deep level, the user needs three things:

- **Knowledge**, captured from high-quality, high-trust resources
- **Skills**, acquired through highly-relevant interactive lessons devised by you, based on the knowledge
- **Wisdom**, which comes from interacting with other learners and practitioners

Before `RESOURCES.md` is well-populated, focus on finding high-quality resources which help the user acquire knowledge. Never trust your parametric knowledge alone — verify against current official docs.

### Fluency vs Storage Strength

Split between two types of learning:

- **Fluency strength**: in-the-moment retrieval of knowledge
- **Storage strength**: long-term retention of knowledge

Fluency can give an illusory sense of mastery; storage strength is the real goal. Design lessons that build long-term retention through desirable difficulty:

- Retrieval practice (recall from memory)
- Spacing (distributing practice over time)
- Interleaving (mixing related topics in skills practice only)

## ELI5 Explainers

Before any dense or foundational lesson, first produce an **ELI5 explainer**: a single HTML page that explains like the user knows nothing about the topic — big pictures, few words. This is the on-ramp; the full lesson builds on it.

An explainer is visual-first: diagrams drawn as inline SVG or simple styled boxes, at most a few dozen words per section. Assume intelligence but zero shared prerequisites — show what problem the thing solves before how it works. Preserve the real mechanism; no forced analogies that break under scrutiny. End with one thing the learner should now be able to predict or do.

Explainers live in `./lessons/` with the same numbering scheme (`000N-<slug>.html`) and link the shared stylesheet in `./assets/`, so they read as part of the course. When a concept later reappears inside a fuller lesson, anchor-link back to its explainer instead of re-explaining in prose.

Use judgment on when it earns its place: new mental models get an explainer; incremental drills do not.

## Lessons

A lesson is the main thing you produce: the unit in which knowledge and skills reach the user. Each lesson is one self-contained HTML file saved to `./lessons/`, titled `0001-<dash-case-name>.html`, incrementing each time.

A lesson should be **beautiful**, with clean, readable typography and layout — think Tufte. Short and completable very quickly: working memory is small, stay within it. Each lesson gives one tangible win, directly tied to the mission, inside the zone of proximal development.

If possible, open the lesson file for the user by running a CLI command (`open`).

Each lesson should link via HTML anchors to other lessons and reference documents, recommend one primary high-trust source to read or watch, and remind the user to ask followup questions — their teacher (the agent) can assist with anything unclear.

## Assets

Lessons are built from reusable **components** stored in `./assets/`: stylesheets, quiz widgets, simulators, diagram helpers — anything a second lesson could reuse.

Reuse is the default. Before authoring a lesson, read `./assets/` and build from existing components. When a lesson needs something new and reusable, write it as a component in `./assets/` and link to it; never inline code a future lesson would duplicate.

A shared stylesheet is the first component every workspace earns: every lesson links it, so lessons look like one consistent course.

## The Mission

Every lesson ties into the mission — the reason the user is learning this topic.

If the mission is unclear or `MISSION.md` is not populated, your first job is to question the user on why they want to learn this. For MLOps-workspace topics, anchor the interview in concrete platform goals (which phase, which service, deploy target) rather than abstract understanding.

Failing to understand the mission makes knowledge acquisition ungrounded and lessons abstract. Missions may change as the user develops — update `MISSION.md` and add a learning record when they do, confirming with the user first.

## Zone Of Proximal Development

Each lesson, the user should feel challenged 'just enough'.

The user may specify exactly what they want to learn. If they don't, figure out their zone of proximal development by reading their `learning-records`, then teach the most relevant thing that fits both the mission and that zone.

## Knowledge

Lessons are designed around a skill the user will learn; the knowledge in a lesson is only what's required for that skill. Teach the knowledge first, then get the user practicing via an interactive feedback loop.

Knowledge comes first from trusted resources tracked in `RESOURCES.md`. Lessons should be littered with citations — links backing up any claim made. For acquiring knowledge, difficulty is the enemy: it eats working memory needed for understanding.

## Skills

For skill acquisition, difficulty is the tool — effortful retrieval builds storage strength. Skills are taught through interactive lessons with tight feedback loops:

- Interactive lessons using quizzes and light in-browser tasks
- Lessons guiding the user through real-world steps (e.g. running actual `helm` commands in a terminal)

Feedback should be immediate and, ideally, automatic.

For quizzes, every answer should be exactly the same number of words (and characters, if possible) — no clues through formatting.

## Acquiring Wisdom

Wisdom comes from real-world interaction. When the user asks a question requiring wisdom, attempt to answer, but ultimately delegate to a **community**: a forum, subreddit, Slack/Discord, or local group where they can test skills against practitioners.

Find high-reputation communities and list them in `RESOURCES.md`. If the user opts out of communities, respect it and record that preference.

## Reference Documents

While creating lessons, also create reference documents — the compressed essence, designed for quick reference. Lessons are rarely revisited; reference documents are.

Good reference candidates: syntax and code snippets, algorithms and flowcharts, CLI command cheatsheets, glossaries for any topic with its own nomenclature. Glossaries are essential: once created, adhere to them in every lesson.
