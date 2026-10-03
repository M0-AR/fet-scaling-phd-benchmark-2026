import subprocess, sys, os
exps = ["exp01_mos_cap_cv.py","exp02_mosfet_iv.py","exp03_scaling_sce.py","exp04_live_market.py"]
base = os.path.dirname(__file__)
for e in exps:
    print("="*20, e)
    r = subprocess.run([sys.executable, os.path.join(base, e)], capture_output=False)
    if r.returncode != 0:
        raise SystemExit(f"FAILED {e}")
print("ALL EXPERIMENTS PASSED")
