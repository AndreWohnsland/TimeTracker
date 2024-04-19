from dataclasses import dataclass
import pandas as pd


@dataclass
class Store:
    df: pd.DataFrame = pd.DataFrame()
