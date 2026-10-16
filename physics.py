"""Core semiconductor equations. Units: cm, eV, V, A, K unless stated."""
from __future__ import annotations

import math

from .materials import Material

Q = 1.602176634e-19        # elementary charge (C)
K_B = 1.380649e-23         # Boltzmann constant (J/K)
EPS0 = 8.8541878128e-14    # vacuum permittivity (F/cm)


def thermal_voltage(temp: float = 300.0) -> float:
    """kT/q in volts (about 0.0259 V at 300 K)."""
    _check_temp(temp)
    return K_B * temp / Q


def band_gap(mat: Material, temp: float = 300.0) -> float:
    """Varshni equation: Eg(T) = Eg0 - alpha*T^2 / (T + beta), in eV."""
    _check_temp(temp)
    return mat.eg0 - mat.alpha * temp**2 / (temp + mat.beta)


def intrinsic_carriers(mat: Material, temp: float = 300.0) -> float:
    """ni = sqrt(Nc*Nv) * exp(-Eg / 2kT), in cm^-3."""
    scale = (temp / 300.0) ** 1.5
    nc, nv = mat.nc300 * scale, mat.nv300 * scale
    return math.sqrt(nc * nv) * math.exp(-band_gap(mat, temp) / (2 * thermal_voltage(temp)))


def carrier_concentrations(mat: Material, nd: float = 0.0, na: float = 0.0, temp: float = 300.0):
    """Return (n, p) in cm^-3 using charge neutrality (full ionisation)."""
    if nd < 0 or na < 0:
        raise ValueError("doping must be non-negative")
    ni = intrinsic_carriers(mat, temp)
    net = nd - na
    if net >= 0:
        n = net / 2 + math.sqrt((net / 2) ** 2 + ni**2)
        p = ni**2 / n
    else:
        p = -net / 2 + math.sqrt((net / 2) ** 2 + ni**2)
        n = ni**2 / p
    return n, p


def resistivity(mat: Material, nd: float = 0.0, na: float = 0.0, temp: float = 300.0) -> float:
    """rho = 1 / (q (mu_n n + mu_p p)), in ohm*cm. Mobilities held constant."""
    n, p = carrier_concentrations(mat, nd, na, temp)
    return 1.0 / (Q * (mat.mu_n * n + mat.mu_p * p))


def built_in_potential(mat: Material, na: float, nd: float, temp: float = 300.0) -> float:
    """Vbi = (kT/q) * ln(Na*Nd / ni^2), in volts."""
    if na <= 0 or nd <= 0:
        raise ValueError("Na and Nd must be positive for a p-n junction")
    return thermal_voltage(temp) * math.log(na * nd / intrinsic_carriers(mat, temp) ** 2)


def depletion_width(mat: Material, na: float, nd: float, bias: float = 0.0, temp: float = 300.0) -> float:
    """Total depletion width in cm. Positive bias = forward bias."""
    vbi = built_in_potential(mat, na, nd, temp)
    if bias >= vbi:
        raise ValueError(f"forward bias {bias} V must stay below Vbi = {vbi:.3f} V")
    eps = mat.eps_r * EPS0
    return math.sqrt(2 * eps * (vbi - bias) / Q * (1 / na + 1 / nd))


def diode_current(v: float, i_s: float = 1e-12, ideality: float = 1.0, temp: float = 300.0) -> float:
    """Shockley equation: I = Is * (exp(V / (n*Vt)) - 1), in amps."""
    if i_s <= 0 or ideality <= 0:
        raise ValueError("Is and ideality factor must be positive")
    return i_s * math.expm1(v / (ideality * thermal_voltage(temp)))


def mosfet_current(vgs: float, vds: float, vth: float, k: float) -> tuple[float, str]:
    """Long-channel NMOS square-law model.

    k = mu * Cox * W / L (A/V^2). Returns (Id in amps, region name).
    """
    if k <= 0:
        raise ValueError("k must be positive")
    vov = vgs - vth
    if vov <= 0:
        return 0.0, "cutoff"
    if vds < vov:
        return k * (vov * vds - vds**2 / 2), "triode"
    return 0.5 * k * vov**2, "saturation"


def _check_temp(temp: float) -> None:
    if temp <= 0:
        raise ValueError("temperature must be above 0 K")
