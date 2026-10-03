"""EXP-01: MOS capacitor C-V (HKUSTx Week 1)."""
import csv, os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from fetlab.physics import mos_cv, oxide_capacitance_per_area

TOX = 2e-9
NA = 1e16
VFB = -0.9

def main(out="benchmarks/results/exp01_cv.csv"):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    vg = [ -2 + i*0.1 for i in range(51) ]  # -2..3 V
    rows = []
    cox = oxide_capacitance_per_area(TOX)
    for v in vg:
        rows.append((v, mos_cv(v, TOX, NA, VFB, True)/cox,
                     mos_cv(v, TOX, NA, VFB, False)/cox))
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Vg_V","C_HF_norm","C_LF_norm"])
        w.writerows(rows)
    # assertions = verification, not hand-tuned
    hf_acc = rows[0][1]; assert abs(hf_acc-1.0) < 1e-9, "accumulation must equal Cox"
    # inversion HF < LF
    assert rows[-1][1] < rows[-1][2], "HF inversion cap < LF inversion cap"
    print(f"EXP01 OK: {len(rows)} points -> {out} Cox={cox:.4e} F/m2")

if __name__ == "__main__":
    main()
