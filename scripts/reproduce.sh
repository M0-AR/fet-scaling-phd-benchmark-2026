#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python3 experiments/exp01_mos_cap_cv.py
python3 experiments/exp02_mosfet_iv.py
python3 experiments/exp03_scaling_sce.py
python3 experiments/exp04_live_market.py
pytest -v
echo "REPRODUCIBLE PIPELINE OK"
