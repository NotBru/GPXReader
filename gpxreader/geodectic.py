from __future__ import annotations 

import numpy as np
import pandas as pd

# Sources:
# - https://en.wikipedia.org/wiki/Geodetic_coordinates
# - https://en.wikipedia.org/wiki/World_Geodetic_System
semi_major_axis = 6378137.000000
semi_minor_axis = 6356752.314245
deg_to_rad = np.pi / 180

def wgs84_to_cartesian(
    latitude: np.array | pd.Series,
    longitude: np.array | pd.Series,
    elevation: np.array | pd.Series | float | int,
) -> dict[str, np.array | series]:

    latitude = deg_to_rad * latitude
    longitude = deg_to_rad * longitude

    N = (
        semi_major_axis ** 2
        / np.sqrt(
            semi_major_axis ** 2 * np.cos(latitude) ** 2
            + semi_minor_axis ** 2 * np.sin(latitude) ** 2
        )
    )

    M = (
        semi_minor_axis ** 2
        / np.sqrt(
            semi_major_axis ** 2 * np.cos(latitude) ** 2
            + semi_minor_axis ** 2 * np.sin(latitude) ** 2
        )
    )

    return {
        "x": (N + elevation) * np.cos(latitude) * np.cos(longitude),
        "y": (N + elevation) * np.cos(latitude) * np.sin(longitude),
        "z": (M + elevation) * np.sin(latitude),
    }

def wgs84_to_displacements(
    latitude: np.array | pd.Series,
    longitude: np.array | pd.Series,
    elevation: np.array | pd.Series | float | int,
) -> dict[str, np.array | series]:

    r = wgs84_to_cartesian(latitude, longitude, elevation)

    de = (
        latitude * 0 if type(elevation) in [float, int]
        else pd.Series(elevation).diff()
    )

    dx, dy, dz = [ r[c].diff() for c in ["x", "y", "z"] ]

    displacement = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    return {
        "horizontal_displacement": np.sqrt(displacement ** 2 - de ** 2),
        "vertical_displacement": de,
        "displacement": displacement,
    }
