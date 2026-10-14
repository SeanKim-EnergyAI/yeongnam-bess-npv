#!/usr/bin/env bash
# Reproduce every table and figure from the committed data/ files.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pytest -q          # case A + case B checks
python3 run_baseline.py       # headline: data validation, per-day LP, NPV, before/after CSVs
python3 run_audit.py          # cap-definition, engine comparison and NPV-bridge tables
python3 run_analytics.py      # per-day LP distribution + NPV=0 frontier figures
python3 run_phase4.py         # representative day: legacy heuristic vs LP
python3 run_phase3.py         # representative-day diagnostic + EXPLORATORY solar scenarios
python3 run_contract_case.py  # case B: break-even contract price + sensitivity
