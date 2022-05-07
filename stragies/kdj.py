import talib
import pandas as pd
from core.config import Config
import os


def check_kdj(csvs):
    for csv in csvs:
        df = pd.read_csv(csv)
        df.set_index("date", drop=True)
        df["k"], df["d"] = talib.STOCH(
            df["high"].values,
            df["low"].values,
            df["close"].values,
            fastk_period=9,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0,
        )
        df["j"] = list(map(lambda x, y: 3 * x - 2 * y, df["k"], df["d"]))


if __name__ == "__main__":
    csv_names = os.listdir(Config.OUTPUT_DIR)
    csvs = [os.path.join(Config.OUTPUT_DIR, csv_name) for csv_name in csv_names]
    check_kdj(csvs=csvs)
