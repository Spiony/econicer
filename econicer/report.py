import pandas as pd
import numpy as np
from pathlib import Path


def reportByYear(acc):

    df = acc.transactions
    yearTrans = pd.pivot_table(df,
                               index=df['date'].dt.year,
                               columns=df['group'],
                               values='value',
                               aggfunc=np.sum)

    filename = Path(acc.settings["plotDir"]) / "summary.csv"

    yearTrans.to_csv(str(filename), sep=";")
