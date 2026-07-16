import argparse
import pandas as pd
from pathlib import Path

def concatenate() -> DataFrame:
    # read files to list
    csv_files = []

    for i in args.input:
        csv_files.append(pd.read_csv(i, index_col=False, header=0))

        if 'Sensor name' not in csv_files[-1].columns:
            csv_files[-1].loc[:, "Sensor name"] = Path(i).name.split('.')[0]

    frame = pd.concat(csv_files, axis=0, ignore_index=True)

    return frame

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', nargs=1)
parser.add_argument('-i', '--input', nargs='+')
args = parser.parse_args()

new_data = concatenate()

new_data.to_csv(args.output[0], index=False)
