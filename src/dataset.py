import pandas as pd

class Dataset:
    def __init__(self, name, df):
        self.name = name
        self.df = df

def load_dataset(name, path):
    df = pd.read_csv(path)
    return Dataset(name, df)