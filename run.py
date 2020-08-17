import json
import merge_data
import organize_data
import pandas as pd

with open('config.json', 'r') as fname:
    config = json.load(fname)

path = config['file_path']

df = merge_data.run(path)
df = organize_data.run(df)
#CSV出力だとうまくいかない
# df.to_csv('./output/merged.csv', index=False)
df.to_excel('./output/merged.xlsx', index=False)