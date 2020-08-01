import date

if __name__ == '__main__':    
    files = date.remove_unncessary_files()
    list_of_tables = date.read_excels(files)
    tables = date.organize_tables(list_of_tables)
    merged_tables = date.merge_tables(tables)
    print(merged_tables.head())