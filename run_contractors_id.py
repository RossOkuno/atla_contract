import json
import add_contractors_id
import pandas as pd

with open('config.json', 'r') as fname:
    config = json.load(fname)

path = config['file_path']

df = pd.read_excel('./output/merged.xlsx')

add_contractors_id.run(df, to_excel=True)