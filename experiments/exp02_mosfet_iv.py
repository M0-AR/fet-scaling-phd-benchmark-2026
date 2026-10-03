"""EXP-02: Classical MOSFET I-V + mobility degradation + velocity saturation (Weeks 3-4)."""
import csv, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from fetlab.physics import mosfet_id, subthreshold_slope_mvdec

W, L, TOX, NA = 1e-6, 0.5e-6, 2e-9, 1e16

def main(out="benchmarks/results/exp02_iv.csv"):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Vgs","Vds","Id_classical","Id_degraded"])
        for vgs in [0.4, 0.7, 1.0, 1.3, 1.8]:
            for i in range(21):
                vds = i * 0.1
                id_cl = mosfet_id(vgs, vds, W, L, TOX, NA, theta_per_v=0.0, esat_vcm=1e9)
                id_dg = mosfet_id(vgs, vds, W, L, TOX, NA, theta_per_v=0.5, esat_vcm=4e4)
                w.writerow([vgs, vds, f"{id_cl:.6e}", f"{id_dg:.6e}"])
    # verify: degraded < classical in saturation; Id increases with Vgs; subthreshold slope ~60-90
    a = mosfet_id(1.8, 1.5, W, L, TOX, NA, theta_per_v=0.0, esat_vcm=1e9)
    b = mosfet_id(1.8, 1.5, W, L, TOX, NA, theta_per_v=0.5, esat_vcm=4e4)
    assert b < a, "mobility+vsat must reduce saturation current"
    c1 = mosfet_id(1.0, 1.5, W, L, TOX, NA)
    c2 = mosfet_id(1.3, 1.5, W, L, TOX, NA)
    assert c2 > c1, "Id must rise with Vgs"
    ss = subthreshold_slope_mvdec(1.25)
    assert 60 < ss < 110, f"SS sanity {ss}"
    print(f"EXP02 OK -> {out} SS(n=1.25)={ss:.1f} mV/dec Isat_cl={a:.3e} Isat_dg={b:.3e}")

if __name__ == "__main__":
    main()
