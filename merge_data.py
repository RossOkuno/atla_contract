import unicodedata
import pandas as pd
import os
import re
from datetime import datetime
import unicodedata

#To remove automaticaly generated file .DSstore, apply following code
def remove_unncessary_files(path):
    files = os.listdir(path)
    if '.DS_Store' in files:
        files.remove('.DS_Store')
        # print('.DS_Store has been successfully removed!')
    else:
        pass
    return files

def read_excels(files, path):
    table_dic = {}
    for filename in files:
        name = filename.replace(".xlsx", "").replace(".xls", "")
        table_dic[name] = pd.read_excel(path + "/" + filename, index=False, encodeing="utf_8")   
    list_of_tables = list(table_dic.values())
    return list_of_tables

# Normalize column names in order to avoid mismatch
def organize_tables(list_of_tables):
    new_tables = []
    for table in list_of_tables:
        columns = []
        dic = {}
        for i in table.columns.values:
            column = unicodedata.normalize("NFKC", i)
            column = column.replace('\n', "")
            columns.append(column)
            dic[i] = column
        table = table.rename(columns=dic)
        new_tables.append(table)    
    return new_tables

# merge all tables
def merge_tables(tables):
    merged_df = pd.concat(tables,ignore_index=True)
    return merged_df

if __name__ == "__main__":
    main()