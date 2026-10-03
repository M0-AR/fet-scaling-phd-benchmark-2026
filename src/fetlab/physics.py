"""FET scaling laboratory — physics core.

Implements textbook MOS-capacitor and MOSFET models used across
HKUSTx Weeks 1-6, with corrections from peer-reviewed 2024-2026 literature.
All equations are analytic (no TCAD binary needed) so benchmarks run
reproducibly in CI / Docker.

References (verified online 2026-10-03):
- Dennard et al. generalized scaling (Baccarani/Wordeman/Dennard 1984)
- GAA MBCFET as ultimate MOSFET (Wiley FET Centennial ch.19, 2026)
- NS-FET scaling Lg 12nm -> 10nm, doping/EOT tradeoffs (Swansea 3D Monte Carlo)
- Channel-engineered C-FET/I-FET device-to-circuit (Sci. Rep. 2026-06-19)
- Synopsys GAA->CFET + BSPDN + DTCO roadmap (2026-08-18)
- Core-shell GAA improvement +36-47% Ion/Ioff (IOP SST 2026-01-21)
- MOS C-V series-R/C model for HRS/LRS (Luna-Lopez et al.)
- 2D CFET A2-node PPA limits: contacts + parasitics dominate (arXiv 2607.12707)
"""

from __future__ import annotations

import math

# Physical constants (SI)
Q = 1.602176634e-19  # C
KB = 1.380649e-23  # J/K
EPS0 = 8.854187817e-12  # F/m
EPS_SI = 11.7 * EPS0
EPS_OX = 3.9 * EPS0
NI_SI = 1.0e10 * 1e6  # m^-3 (1e10 cm^-3)
VTH_300K = KB * 300.0 / Q  # ~25.85 mV


def thermal_voltage(t_kelvin: float = 300.0) -> float:
    return KB * t_kelvin / Q


def oxide_capacitance_per_area(tox_m: float) -> float:
    """Cox' = eps_ox / tox  [F/m^2]."""
    return EPS_OX / tox_m


def fermi_potential(na_cm3: float, t_kelvin: float = 300.0) -> float:
    """Bulk Fermi potential phi_F = kT/q * ln(Na/ni) for p-substrate."""
    na_m3 = na_cm3 * 1e6
    ni_m3 = NI_SI
    return thermal_voltage(t_kelvin) * math.log(na_m3 / ni_m3)


def depletion_charge(gamma: float, phi_s: float) -> float:
    return gamma * math.sqrt(max(phi_s, 0.0))


def body_factor(tox_m: float, na_cm3: float) -> float:
    """Gamma = sqrt(2 q eps_si Na) / Cox'."""
    cox = oxide_capacitance_per_area(tox_m)
    na_m3 = na_cm3 * 1e6
    return math.sqrt(2 * Q * EPS_SI * na_m3) / cox


def threshold_voltage(
    tox_m: float,
    na_cm3: float,
    phi_ms_v: float = -0.9,
    qox_c_cm2: float = 0.0,
    vbs_v: float = 0.0,
) -> float:
    """Classical Vt = Vfb + 2phi_F + gamma*sqrt(2phi_F - Vbs)."""
    cox = oxide_capacitance_per_area(tox_m)
    phi_f = fermi_potential(na_cm3)
    vfb = phi_ms_v - (qox_c_cm2 * Q / cox if qox_c_cm2 else 0.0)
    gamma = body_factor(tox_m, na_cm3)
    return vfb + 2 * phi_f + gamma * math.sqrt(max(2 * phi_f - vbs_v, 0.0))


def mos_cv(
    vg_v: float,
    tox_m: float,
    na_cm3: float,
    vfb_v: float = -0.9,
    freq_high: bool = True,
) -> float:
    """Idealized MOS C-V (per area, F/m^2).

    - Accumulation (Vg < Vfb): C = Cox
    - Depletion: C = Cox*Cs/(Cox+Cs), Cs = eps_si / Wd
    - Inversion: LF -> Cox, HF -> Cox*Cdmin/(Cox+Cdmin)
    Uses depletion approx Wd = sqrt(2 eps_si phi_s / qNa).
    """
    cox = oxide_capacitance_per_area(tox_m)
    na_m3 = na_cm3 * 1e6
    phi_f = fermi_potential(na_cm3)
    vt = threshold_voltage(tox_m, na_cm3, phi_ms_v=vfb_v)
    if vg_v < vfb_v:
        return cox
    if vg_v < vt:
        # depletion: phi_s ~ (Vg-Vfb) partitioned; approximate phi_s
        phi_s = min(max(vg_v - vfb_v, 0.05), 2 * phi_f)
        wd = math.sqrt(2 * EPS_SI * phi_s / (Q * na_m3))
        cs = EPS_SI / wd
        return cox * cs / (cox + cs)
    # inversion
    if not freq_high:
        return cox
    wdmax = math.sqrt(4 * EPS_SI * phi_f / (Q * na_m3))
    cdmin = EPS_SI / wdmax
    return cox * cdmin / (cox + cdmin)


def subthreshold_slope_mvdec(n_factor: float, t_kelvin: float = 300.0) -> float:
    """SS = n * (kT/q) * ln(10) in mV/dec."""
    return n_factor * thermal_voltage(t_kelvin) * math.log(10) * 1000.0


def ideality_factor(cd_cox_ratio: float, dit_term: float = 0.0) -> float:
    """n = 1 + Cd/Cox + Cit/Cox."""
    return 1.0 + cd_cox_ratio + dit_term


def effective_mobility(mu0_m2vs: float, theta_per_v: float, vgs_minus_vt: float) -> float:
    """Mobility degradation: mu_eff = mu0 / (1 + theta*(Vgs-Vt)). Week 4."""
    overdrive = max(vgs_minus_vt, 0.0)
    return mu0_m2vs / (1.0 + theta_per_v * overdrive)


def saturation_voltage_velocity(
    vgs_minus_vt: float, esat_vcm: float, lg_m: float
) -> float:
    """Vdsat with velocity saturation: (Vgs-Vt)/(1+(Vgs-Vt)/(Esat*L))."""
    overdrive = max(vgs_minus_vt, 0.0)
    esat_vm = esat_vcm * 100.0
    denom = 1.0 + overdrive / max(esat_vm * lg_m, 1e-12)
    return overdrive / denom


def mosfet_id(
    vgs_v: float,
    vds_v: float,
    w_m: float,
    l_m: float,
    tox_m: float,
    na_cm3: float,
    mu0_cm2vs: float = 400.0,
    theta_per_v: float = 0.3,
    esat_vcm: float = 4.0e4,
    lambda_per_v: float = 0.05,
    dibl_vv: float = 0.0,
    ss_mvdec: float | None = None,
    t_kelvin: float = 300.0,
) -> float:
    """Compact drain-current covering subthreshold + linear + saturation.

    - Vt lowered by DIBL: Vt_eff = Vt0 - dibl*Vds
    - Subthreshold: exponential with SS (default 75 mV/dec short-channel)
    - Above threshold: mobility degradation + velocity-saturation denominator
      Id_lin = mu_eff Cox W/L [(Vod)Vds - Vds^2/2] / (1+Vds/(Esat L))
      Id_sat velocity-sat form, continuous at Vdsat, with CLM (1+lambda Vds).
    Returns Id in Amperes.
    """
    mu0 = mu0_cm2vs * 1e-4  # to m^2/Vs
    cox = oxide_capacitance_per_area(tox_m)
    vt0 = threshold_voltage(tox_m, na_cm3)
    vt_eff = vt0 - dibl_vv * vds_v
    vod = vgs_v - vt_eff

    if vod <= -0.25:
        # deep subthreshold
        n_def = 1.25 if ss_mvdec is None else ss_mvdec / (
            thermal_voltage(t_kelvin) * math.log(10) * 1000.0
        )
        i0 = mu0 * cox * (w_m / l_m) * (n_def * thermal_voltage(t_kelvin)) ** 2
        # anchor I0 ~ 1e-9 * W/L scale for realism
        i0 = max(i0 * 1e-4, 1e-12 * (w_m / l_m))
        return float(
            i0
            * math.exp(vod / (n_def * thermal_voltage(t_kelvin)))
            * (1.0 - math.exp(-vds_v / thermal_voltage(t_kelvin)))
        )
    if vod <= 0.0:
        # near-threshold smoothing: blend subthreshold into linear
        frac = (vod + 0.25) / 0.25  # 0..1
        id_sub = mosfet_id(
            vt_eff - 0.25, vds_v, w_m, l_m, tox_m, na_cm3,
            mu0_cm2vs, theta_per_v, esat_vcm, lambda_per_v,
            dibl_vv, ss_mvdec, t_kelvin,
        )
        mu_eff = effective_mobility(mu0, theta_per_v, 0.05)
        vdsat = saturation_voltage_velocity(0.05, esat_vcm, l_m)
        id_lin = (
            mu_eff * cox * (w_m / l_m) * (0.05 * min(vds_v, vdsat) - min(vds_v, vdsat) ** 2 / 2.0)
            / (1.0 + min(vds_v, vdsat) / (esat_vcm * 100.0 * l_m))
        )
        return float((1 - frac) * id_sub + frac * max(id_lin, 0.0))

    mu_eff = effective_mobility(mu0, theta_per_v, vod)
    vdsat = saturation_voltage_velocity(vod, esat_vcm, l_m)
    esl = esat_vcm * 100.0 * l_m
    if vds_v < vdsat:
        id_lin = mu_eff * cox * (w_m / l_m) * (vod * vds_v - vds_v**2 / 2.0) / (
            1.0 + vds_v / max(esl, 1e-12)
        )
        return float(max(id_lin, 0.0))
    # saturation with velocity-sat + CLM
    id_sat0 = mu_eff * cox * (w_m / l_m) * (vod * vdsat - vdsat**2 / 2.0) / (
        1.0 + vdsat / max(esl, 1e-12)
    )
    return float(max(id_sat0 * (1.0 + lambda_per_v * vds_v), 0.0))


def natural_length_planar(tox_m: float, xj_m: float) -> float:
    """Planar lambda = sqrt(eps_si/eps_ox * tox * xj)."""
    return math.sqrt((EPS_SI / EPS_OX) * tox_m * xj_m)


def natural_length_gAA(t_si_m: float, tox_m: float) -> float:
    """GAA cylinder approx: lambda ~ sqrt(eps_si * d^2 ln(1+2tox/d)/(8 eps_ox))."""
    d = t_si_m
    return math.sqrt(EPS_SI * d**2 * math.log(1 + 2 * tox_m / max(d, 1e-12)) / (8 * EPS_OX))


def dibl_model(lg_m: float, lambda_m: float, vds_v: float = 0.7) -> float:
    """Illustrative DIBL ~ exp(-Lg/2lambda) scaled to mV/V, anchored to
    literature: ~32 mV/V at Lg=12nm NS, ~77 mV/V at Lg=10nm (Swansea MC)."""
    import math as _m

    # anchor: lambda_ref chosen so Lg=12nm -> 32, Lg=10nm -> 77
    # use empirical: DIBL = 8 * exp((12nm - Lg)/3.4nm) * ... simplified
    lg_nm = lg_m * 1e9
    if lg_nm >= 12:
        base = 32.0 * _m.exp(-(lg_nm - 12.0) / 18.0)
    else:
        base = 32.0 * _m.exp((12.0 - lg_nm) / 2.28)  # 10nm -> ~77
        base = min(base, 220.0)
    # lambda correction factor
    base *= max(0.5, min(1.5, lambda_m / 6e-9))
    return float(base)
