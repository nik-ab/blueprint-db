import pandas as pd


class Dataset:
    def __init__(self, name, df):
        self.name = name
        self.df = df


def load_dataset(name, path):
    df = pd.DataFrame()
    try:
        df = pd.read_csv(path, nrows=1000)
    except Exception as _:
        pass

    return Dataset(name, df)
