"""Technology scaling tables + Moore/Dennard analytics.

Node data compiled from IRDS + IEDM/VLSI 2023-2026 literature surveyed
2026-10-03 (see README references). Values are representative, not
foundry-confidential; all sources cited in README/paper.
"""

from __future__ import annotations

NODES = [
    # node, Lg(nm), CPP(nm), EOT(nm), Vdd(V), arch
    ("45nm", 35, 190, 1.2, 1.0, "planar+HKMG"),
    ("28nm", 27, 120, 1.0, 0.9, "planar+HKMG"),
    ("14nm", 20, 70, 0.9, 0.8, "FinFET"),
    ("10nm", 18, 54, 0.85, 0.75, "FinFET"),
    ("7nm", 16, 54, 0.8, 0.75, "FinFET"),
    ("5nm", 15, 48, 0.75, 0.72, "FinFET"),
    ("3nm", 12, 44, 0.9, 0.70, "GAA-NS"),
    ("2nm", 10, 42, 0.9, 0.65, "GAA-NS+BSPDN"),
    ("A14", 10, 38, 0.85, 0.60, "GAA-NS/CFET-demo"),
    ("A2-CFET", 10, 36, 0.8, 0.55, "CFET/2D-demo"),
]

# Historical transistor counts (public, Moore plot) for regression
MOORE_DATA = [
    (1971, 2.3e3, "4004"),
    (1978, 2.9e4, "8086"),
    (1989, 1.18e6, "486"),
    (2000, 4.2e7, "Pentium4"),
    (2010, 1.17e9, "POWER7"),
    (2017, 1.9e10, "M1-Ultra-class"),
    (2020, 5.4e10, "A14"),
    (2022, 1.14e11, "M1-Ultra/4090-class"),
    (2024, 2.08e11, "Blackwell-class"),
    (2026, 3.0e11, "Rubin/A16-class-est"),
]


def dennard_scale(factor: float = 0.7) -> dict:
    """Classical Dennard scaling for linear shrink factor kappa=1/factor."""
    kappa = 1.0 / factor
    return {
        "L/W/tox_scale": factor,
        "doping_scale": kappa,
        "voltage_scale": factor,
        "current_scale": factor,
        "delay_scale": factor,
        "power_density_const": 1.0,
        "density_scale": kappa**2,
    }


def moore_doubling_years(counts: list | None = None) -> float:
    """Fit log2(count) vs year -> years per doubling (least squares)."""
    import math

    data = counts or MOORE_DATA
    n = len(data)
    xs = [y for y, _, _ in data]
    ys = [math.log2(c) for _, c, _ in data]
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sxy / sxx  # doublings per year
    return 1.0 / slope if slope else float("inf")


def node_table_markdown() -> str:
    lines = ["| Node | Lg (nm) | CPP (nm) | EOT (nm) | Vdd (V) | Arch |",
             "|---|---|---|---|---|---|"]
    for node, lg, cpp, eot, vdd, arch in NODES:
        lines.append(f"| {node} | {lg} | {cpp} | {eot} | {vdd} | {arch} |")
    return "\n".join(lines)
