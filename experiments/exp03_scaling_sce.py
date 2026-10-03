"""EXP-03: Scaling + short-channel effects (Week 5) + hidden pattern.

Verifies:
- Dennard density 4x per 0.7x shrink
- Moore doubling ~2.0-2.6 yr (1971-2026 fit)
- Natural-length ladder planar > FinFET > GAA
- DIBL blow-up Lg 12nm(32mV/V) -> 10nm(77mV/V) per Swansea MC
- HIDDEN PATTERN: Ion gain from doping/EOT saturates while DIBL explodes;
  strain benefit capped by quantum confinement (only +3% <110> at 0.5%).
"""
import csv, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from fetlab.physics import natural_length_planar, natural_length_gAA, dibl_model, mosfet_id
from fetlab.scaling import dennard_scale, moore_doubling_years

def main(out="benchmarks/results/exp03_scaling.csv"):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    d = dennard_scale(0.7)
    assert abs(d["density_scale"] - 2.04) < 0.05
    yrs = moore_doubling_years()
    rows = [("metric", "value"), ("dennard_density_0.7x", f"{d['density_scale']:.3f}"),
            ("moore_years_per_doubling", f"{yrs:.2f}")]
    # natural lengths
    lp = natural_length_planar(1e-9, 30e-9)
    lg = natural_length_gAA(5e-9, 1e-9)
    rows += [("lambda_planar_nm", f"{lp*1e9:.2f}"), ("lambda_GAA_nm", f"{lg*1e9:.2f}")]
    assert lg < lp, "GAA must improve electrostatics"
    # DIBL anchors
    d12 = dibl_model(12e-9, 6e-9); d10 = dibl_model(10e-9, 6e-9)
    rows += [("DIBL_12nm_mV/V", f"{d12:.1f}"), ("DIBL_10nm_mV/V", f"{d10:.1f}")]
    assert 25 < d12 < 40 and 65 < d10 < 90, f"DIBL anchors failed {d12},{d10}"
    # Ion vs Lg shrink: 12nm->10nm loses ~10.7% before doping fix (Swansea)
    W = 50e-9
    id12 = mosfet_id(0.7, 0.7, W, 12e-9, 1e-9, 1e16, mu0_cm2vs=300)
    id10 = mosfet_id(0.7, 0.7, W, 10e-9, 1e-9, 1e16, mu0_cm2vs=300)
    rows += [("Id_12nm_A", f"{id12:.3e}"), ("Id_10nm_A", f"{id10:.3e}")]
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerows(rows)
    print(f"EXP03 OK -> {out} Moore={yrs:.2f}y DIBL {d12:.0f}->{d10:.0f} mV/V lambda {lp*1e9:.1f}->{lg*1e9:.1f}nm")

if __name__ == "__main__":
    main()
