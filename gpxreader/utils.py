import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from gpxreader.read import read

mps_to_kmph = 3.6

def with_derived_data(dataset: pd.DataFrame) -> pd.DataFrame:
    dataset = dataset.copy()

    dataset["distance"] = dataset["horizontal_displacement"].cumsum()

    dt = (dataset["datetime"].astype("int") / 10 ** 9).diff()

    prefixes = ["", "horizontal_", "vertical_"]
    for prefix in prefixes:
        dataset[f"{prefix}speed"] = (
            dataset[f"{prefix}displacement"] / dt * mps_to_kmph
        )

    dataset["slope"] = (
        dataset["vertical_displacement"] / dataset["horizontal_displacement"]
    )

    return dataset
