from typing import TextIO
import re

import pandas as pd

_num = r"(-?\d+\.\d+)"
_time = r"(\d+-\d+-\d+T\d+:\d+:\d+\w)"
datapoint_pattern = re.compile(
    f'"{_num}" lon="{_num}">.*?<ele>{_num}</ele>'
    + f'.*?<time>{_time}',
    re.DOTALL
)

def parse(text: str):
    numeric = ["latitude", "longitude", "elevation"]
    datapoints = datapoint_pattern.findall(text)
    dataframe = pd.DataFrame(
        data=datapoints,
        columns=[*numeric, "datetime"],
    ).astype({**{c: "float64" for c in numeric}, "datetime": "datetime64[ns]"})

    return dataframe[["datetime", *numeric]]

def read(file_or_filename: TextIO | str):
    if isinstance(file_or_filename, str):
        with open(file_or_filename, "r") as inf:
            return parse(inf.read())
    return parse(file_or_filename.read())
