import json

import pandas as pd

from cleansing import merge_data
from cleansing import organize_data

def main():
    with open('./config/config.json', 'r') as fname:
        config = json.load(fname)
    path = config['file_path']
    df = merge_data.main(path)
    df = organize_data.main(df)

    #CSV出力だとうまくいかない
    # df.to_csv('./output/merged.csv', index=False)
    df.to_excel('./output/merged.xlsx', index=False)


if __name__ == "__main__":
    main()