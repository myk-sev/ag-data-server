import argparse
import pandas as pd
from pathlib import Path

def concatenate() -> DataFrame:
    csv_files = []

    for i in args.input:
        new_file: DataFrame = pd.read_csv(i, index_col=False, header=0)

        # TODO: specify pre-conversion time formats
        if 'Timestamp for sample frequency every 1 min min' in new_file.columns:
            new_file["Time"] = pd.to_datetime(new_file['Timestamp for sample frequency every 1 min min'])
            new_file.drop(columns=['Timestamp for sample frequency every 1 min min'], inplace=True)

        if 'Time(DD/MM/YYYY h:mm:ss A)' in new_file.columns:
            new_file["Time"] = pd.to_datetime(new_file['Time(DD/MM/YYYY h:mm:ss A)'])
            new_file.drop(columns=['Time(DD/MM/YYYY h:mm:ss A)'], inplace=True)

        if 'Sensor name' not in new_file.columns:
            new_file.loc[:, "Sensor name"] = Path(i).name.split('.')[0]

        csv_files.append(new_file)

    frame = pd.concat(csv_files, axis=0, ignore_index=True)

    frame.drop_duplicates(subset=["Time", "Sensor name"], inplace=True)

    return frame

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', nargs=1)
parser.add_argument('-i', '--input', nargs='+')
args = parser.parse_args()

new_data = concatenate()

new_data.to_csv(args.output[0], index=False)
