"""EXP-04: Live-market verification (Weeks 5-6 economics of scaling).

Uses pinned live snapshots 2026-10-03 (TSM/INTC/NVDA) + Intel 10-K.
Attempts best-effort live refresh; benchmark passes offline (reproducible).
Asserts real-world facts that any public scaling claim must survive:
- NVDA mcap > TSM despite same leading node (fabless capture)
- Intel revenue 2021->2025 down >25%, 2024 net loss ~-18.7B (scaling cost wall)
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from fetlab.live_verify import QUOTES, INTEL_FUNDAMENTALS, economics_vs_scaling, try_live_refresh

def main(out="benchmarks/results/exp04_live.json"):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    live = try_live_refresh()
    eco = economics_vs_scaling()
    # hard verification on pinned public data
    assert QUOTES["NVDA"]["mcap"] > QUOTES["TSM"]["mcap"], "NVDA>TSM mcap on snapshot"
    rev_drop = eco["intel_revenue_drop_21_25"]
    assert rev_drop > 0.25, f"Intel revenue drop expected >25%, got {rev_drop}"
    assert INTEL_FUNDAMENTALS["net_income"][2024] < 0, "Intel 2024 must be loss-making"
    payload = {"snapshot_quotes": QUOTES, "economics": eco, "live_refresh_best_effort": live}
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"EXP04 OK -> {out} NVDA {QUOTES['NVDA']['mcap']/1e12:.2f}T > TSM {QUOTES['TSM']['mcap']/1e12:.2f}T; Intel rev-drop {rev_drop*100:.1f}%")

if __name__ == "__main__":
    main()
