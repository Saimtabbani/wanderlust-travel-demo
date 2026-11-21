# Reproducible ranking check

Run this check with the same catalogue and code revision:

```bash
py backend/evaluate_recommendations.py
```

It reads the versioned `queries.v1.json` fixture, runs the current ranker, and writes `latest-results.json` (intentionally ignored by Git). It reports MRR and NDCG@10 per query.

This is only a repeatable engineering check. It does **not** establish recommendation quality, user benefit, novelty, or publication readiness. A defensible research evaluation still needs preregistered or clearly stated hypotheses, a properly licensed/consented dataset, independently labelled or behavioural relevance data, appropriate baselines, a held-out test set, uncertainty/significance analysis, and documented ethics/privacy procedures.
