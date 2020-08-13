import json
import merge_data
import organize_data
import pandas as pd

with open('config.json', 'r') as fname:
    config = json.load(fname)

path = config['file_path']

if __name__ == '__main__':    
    files = merge_data.remove_unncessary_files(path=path)
    list_of_tables = merge_data.read_excels(files=files, path=path)
    tables = merge_data.organize_tables(list_of_tables)
    df = merge_data.merge_tables(tables)
    df = organize_data.tmp(df)
    df.to_csv('./output/merged.csv', index=False)