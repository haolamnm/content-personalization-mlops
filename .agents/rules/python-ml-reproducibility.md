---
description: Reproducibility discipline for ML experiments — seeds, MLflow runs, point-in-time correctness
globs: ["**/*.py", "**/*.ipynb"]
alwaysApply: false
---

# Rule: Python ML Reproducibility

## Constraints

- **An experiment without an MLflow run did not happen** ([Principle 5](../../AGENTS.md)): every training/tuning execution logs params, metrics, and the git SHA of `platform/` to MLflow before any claim is made.
- **Seeds are explicit and logged**: random_state/np seed/torch seed set once at entrypoint and recorded as a param; unseeded randomness in training code is banned.
- **Training data comes only through Feast point-in-time joins** ([CONTEXT-MAP](../../CONTEXT-MAP.md) §2) — ad-hoc Iceberg queries that risk feature leakage are banned; leakage checks (as-of correctness) are part of dataset validation.
- **Datasets are versioned artifacts**: training inputs reference an immutable snapshot (Iceberg snapshot ID or materialized path), never "latest table".
- Model promotion is a registry decision: candidate → staging on measured offline metrics, → production only with the promotion criteria written down first.
