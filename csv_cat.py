import argparse
import csv
import pandas as pd

def concatenate() -> DataFrame:
    # read files to list
    csv_files = []

    for i in args.input:
        csv_files.append(pd.read_csv(i, index_col=None, header=0))

    frame = pd.concat(csv_files, axis=0, ignore_index=True)

    return frame

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', nargs=1)
parser.add_argument('-i', '--input', nargs='+')
args = parser.parse_args()

new_data = concatenate()

new_data.to_csv(args.output[0])
