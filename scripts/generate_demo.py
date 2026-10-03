"""Generate demo visuals: PNG charts + animated GIF for README/preview.html."""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

ROOT = os.path.join(os.path.dirname(__file__), "..")
RES = os.path.join(ROOT, "benchmarks", "results")
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

def load_cv():
    vg, hf, lf = [], [], []
    with open(os.path.join(RES, "exp01_cv.csv")) as f:
        r = csv.DictReader(f)
        for row in r:
            vg.append(float(row["Vg_V"])); hf.append(float(row["C_HF_norm"])); lf.append(float(row["C_LF_norm"]))
    return vg, hf, lf

def load_iv():
    from collections import defaultdict
    curves = defaultdict(list)
    with open(os.path.join(RES, "exp02_iv.csv")) as f:
        r = csv.DictReader(f)
        for row in r:
            curves[float(row["Vgs"])].append((float(row["Vds"]), float(row["Id_degraded"])))
    return curves

def main():
    vg, hf, lf = load_cv()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(vg, hf, label="High-freq", linewidth=2)
    ax.plot(vg, lf, "--", label="Low-freq", linewidth=2)
    ax.set_xlabel("Gate voltage Vg (V)"); ax.set_ylabel("C / Cox")
    ax.set_title("EXP-01 MOS C-V: accumulation=Cox, HF vs LF split in inversion")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(ASSETS, "demo_cv.png"), dpi=150)
    plt.close(fig)

    curves = load_iv()
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    for vgs, pts in sorted(curves.items()):
        x = [p[0] for p in pts]; y = [p[1]*1e3 for p in pts]
        ax2.plot(x, y, label=f"Vgs={vgs}V")
    ax2.set_xlabel("Vds (V)"); ax2.set_ylabel("Id (mA, W=1um)")
    ax2.set_title("EXP-02 MOSFET I-V with mobility + velocity saturation")
    ax2.legend(fontsize=8); ax2.grid(alpha=0.3)
    fig2.tight_layout(); fig2.savefig(os.path.join(ASSETS, "demo_iv.png"), dpi=150)
    plt.close(fig2)

    # Animated GIF: C-V sweep dot moving (6s, 12fps, small)
    fig3, ax3 = plt.subplots(figsize=(6, 3.4))
    ax3.plot(vg, hf, linewidth=2)
    ax3.set_xlim(min(vg), max(vg)); ax3.set_ylim(0, 1.1)
    ax3.set_xlabel("Vg (V)"); ax3.set_ylabel("C/Cox (HF)")
    ax3.set_title("MOS C-V sweep demo")
    dot, = ax3.plot([], [], "ro", ms=8)
    def upd(i):
        dot.set_data([vg[i]], [hf[i]]); return (dot,)
    ani = animation.FuncAnimation(fig3, upd, frames=len(vg), interval=120, blit=True)
    ani.save(os.path.join(ASSETS, "demo.gif"), writer="pillow", fps=12)
    plt.close(fig3)
    print("demo assets OK:", sorted(os.listdir(ASSETS)))

if __name__ == "__main__":
    main()
