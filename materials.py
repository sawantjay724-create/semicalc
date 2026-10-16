"""Material parameters at ~300 K (textbook values, approximate)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Material:
    name: str
    eg0: float        # band gap at 0 K (eV)
    alpha: float      # Varshni alpha (eV/K)
    beta: float       # Varshni beta (K)
    nc300: float      # conduction-band effective density of states (cm^-3)
    nv300: float      # valence-band effective density of states (cm^-3)
    eps_r: float      # relative permittivity
    mu_n: float       # electron mobility (cm^2/V/s), lightly doped
    mu_p: float       # hole mobility (cm^2/V/s), lightly doped


MATERIALS = {
    "si": Material("Silicon", 1.170, 4.73e-4, 636, 2.8e19, 1.04e19, 11.7, 1350, 480),
    "ge": Material("Germanium", 0.7437, 4.77e-4, 235, 1.04e19, 6.0e18, 16.0, 3900, 1900),
    "gaas": Material("Gallium Arsenide", 1.519, 5.405e-4, 204, 4.7e17, 7.0e18, 12.9, 8500, 400),
}


def get_material(key: str) -> Material:
    try:
        return MATERIALS[key.lower()]
    except KeyError:
        raise ValueError(f"unknown material '{key}'. Choose from: {', '.join(MATERIALS)}") from None
