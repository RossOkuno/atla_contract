import json
from cleansing import add_contractors_id
import pandas as pd

def main():
    with open('./config/config.json', 'r') as fname:
        config = json.load(fname)

    path = config['file_path']

    df = pd.read_excel('./output/merged.xlsx')

    add_contractors_id.main(df, to_excel=True)


if __name__ == "__main__":
    main()