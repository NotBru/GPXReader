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
    """Convert WGS84 coordinates to cartesian coordinates

    Parameters
    ----------
    latitude : np.array | pd.Series
        Latitude array
    longitude : np.array | pd.Series
        Longitude array
    elevation : np.array | pd.Series | float | int
        Elevation array or, if constant, scalar

    Returns
    -------
    dict[str, np.array | series] :
        dict with "x", "y", and "z" keys, and their corresponding series
    """

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

def process_wgs84(
    latitude: np.array | pd.Series,
    longitude: np.array | pd.Series,
    elevation: np.array | pd.Series | float | int,
    smoothing: (int, int, int) = (0, 0, 0)
) -> dict[str, np.array | series]:
    """Obtain cartesian coordinates and displacements. Smoothing is performed
    beforehand.

    Parameters
    ----------
    latitude : np.array | pd.Series
        Latitude array
    longitude : np.array | pd.Series
        Longitude array
    elevation : np.array | pd.Series | float | int
        Elevation array or, if constant, scalar
    smoothing : (int, int, int)
        Length of smoothing kernel for lat, lon, and elevation series.
    """

    def smoothen(a: np.array | pd.Series, l: int):
        if l <= 1:
            return a
        x = np.linspace(-2, 2, l)
        ker = np.exp(-.5 * x ** 2)
        ker /= np.sum(ker)
        convolution = np.convolve(a, ker, mode="same")
        if isinstance(a, np.array):
            return convolution
        return pd.Series(convolution, index=a.index, name=a.name)

    latitude = smoothen(latitude, smoothing[0])
    longitude = smoothen(longitude, smoothing[1])
    elevation = smoothen(elevation, smoothing[2])

    r = wgs84_to_cartesian(latitude, longitude, elevation)

    de = (
        latitude * 0 if type(elevation) in [float, int]
        else pd.Series(elevation).diff()
    )

    dx, dy, dz = [ r[c].diff() for c in ["x", "y", "z"] ]

    displacement = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    return {
        **r,
        "horizontal_displacement": np.sqrt(np.max(displacement ** 2 - de ** 2, 0)),
        "vertical_displacement": de,
        "displacement": displacement,
    }
