# METHODS — zero-to-hero verification protocol

1. Search online first (one at a time, distinct keywords, log failures).
2. Pin the date (2026-10-03 UTC) and snapshot live data (quotes + 10-K).
3. Write analytic models with in-code assertions (no hand-tuned plots).
4. Run `bash scripts/reproduce.sh`; fix models, never edit outputs.
5. Dockerize (`docker compose up --build`) and re-run pytest inside.
6. Publish repo + image; invite falsification via H1/H2 criteria.

CCD/CMOS-APS note: CCD = MOS-capacitor shift register (charge coupling);
APS = per-pixel source-follower + reset/select (MOS+source, Week 2).
Our C-V + body-effect models are the quantitative substrate; full
optoelectronic Monte Carlo is listed as extension.
