import unicodedata
import pandas as pd
import os
import re
from datetime import datetime
import unicodedata

#To remove automaticaly generated file .DSstore, apply following code
def remove_unncessary_files(path = "./origanized_jmod_contract_data"):
    files = os.listdir(path)
    if '.DS_Store' in files:
        files.remove('.DS_Store')
        # print('.DS_Store has been successfully removed!')
    else:
        pass
    return files

def read_excels(files, path = "./origanized_jmod_contract_data"):
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

def make_JFY_column(date) :
    #return:Fiscal year (month, day not included) input:date (timestamp) 
    end_month_fy = 3
    if date.month <= end_month_fy:
        fy = date.year - 1 
        return  fy
    else:
        fy = date.year
        return fy 

# Incorporate 3columns and make a "contracotor" colunm
def add_contractor_column(merged):
    #create contractor column
    name1 = "契約相手方の名称"
    name2 = "契約の相手方の商号又は名称及び住所"
    name3 = "契約相手方の商号又は名称及び住所"
    merged["contractor"] = merged[name1]
    merged["contractor"][merged["contractor"].isnull()] = merged[name2][merged["contractor"].isnull()]
    merged["contractor"][merged["contractor"].isnull()] = merged[name3][merged["contractor"].isnull()]

    contractor_list = []
    for i in merged["contractor"]:
        text = re.search('\S+',str(i)).group()
        contractor_list.append(text)
    merged["contractor"] = contractor_list
    return merged

def remove_null_no_amount(merged):
    removed_merged = merged.dropna(subset=['契約金額(円)'])
    return removed_merged

#列名を正規化
def normalize_columns(removed_merged):
    exclude_cols =  ['予定価格(円)', '再就職の役員の数', '契約金額(円)','契約締結日', '応札・応募者数', '数量', '落札率', "法人番号"]
    target_cols = [col for col in removed_merged.columns if col not in exclude_cols]
    for i in target_cols:
        try:
            removed_merged[i] = removed_merged[i].str.normalize("NFKC")
        except:
            print("skipped", i)
    return removed_merged
    
# ADD JFY column 
def add_jfy(removed_merged):
    JFY = []
    JFY = removed_merged['契約締結日'].apply(make_JFY_column)
    removed_merged["JFY"] = JFY
    return removed_merged

# create Initial_cost column to understand if the contract is for initial (development) not production
def add_initial_cost(removed_merged):
    removed_merged["initial_cost"] = ""
    target_word = "初度費"
    removed_merged["initial_cost"] = [target_word in i for i in removed_merged["物品役務等の名称"]]
    return removed_merged

# create R%D column
def add_randd(removed_merged):
    list_items = list(removed_merged["物品役務等の名称"])
    list_RandD = []
    target_word = "調査研究"
    target_word2 = "研究試作"
    for i in range(len(removed_merged)):
        item = str(list_items[i])
        if target_word in item:
            list_RandD.append(True)
        elif target_word2 in item:
            list_RandD.append(True)    
        else:
            list_RandD.append(False)
    removed_merged["R&D"] = list_RandD
    return removed_merged
            
# create unit_price column
def add_randd(removed_merged):
    removed_merged["unit_price"] = round(removed_merged["契約金額(円)"] / removed_merged["数量"])
    return removed_merged

# create MDA column
def add_MDA(removed_merged):
    target_text = "(MDA)"
    list1 = list(removed_merged["随意契約によることとした会計法令の根拠条文及び理由"])
    list2 = list(removed_merged["随意契約によることとした会計法令の根拠条文及び理由(企画競争又は公募)"])
    list_MDA = []
    for i in range(len(removed_merged)):
        text = list1[i]
        text2 = list2[i]
        if (target_text in str(text)) == True:
            list_MDA.append(True)

        elif (target_text in str(text2)) == True:
            list_MDA.append(True)

        else:
            list_MDA.append(False)

    removed_merged["MDA"] = list_MDA
    return removed_merged

# "competition"と"reason_non_competiotin"の列を追加
def add_competition(removed_merged):
    removed_merged["competition"] = removed_merged["一般競争入札・指名競争入札の別(総合評価の実施)"].notnull()
    removed_merged["reason_non_competiotin"] = removed_merged["随意契約によることとした会計法令の根拠条文及び理由"]
    removed_merged["reason_non_competiotin"][removed_merged["reason_non_competiotin"].isnull()] = removed_merged["随意契約によることとした会計法令の根拠条文及び理由(企画競争又は公募)"][removed_merged["reason_non_competiotin"].isnull()]
    return removed_merged

# Remove balanks from 物品役務等の名称 and contractor
def remove_blankrows(removed_merged):
    strip_target = ["物品役務等の名称", "contractor", "reason_non_competiotin"]
    for column in strip_target:
        target = list(removed_merged.loc[:,column][removed_merged.loc[:,column].notnull()])
        stripped = [i.strip() for i in target]
        stripped = [i.replace("\r\n", "") for i in stripped]
        stripped = [i.replace("\n", "") for i in stripped]
        stripped = [i.replace("\'", "") for i in stripped]
        stripped = [i.replace("\"", "") for i in stripped]
        removed_merged.loc[:,column][removed_merged.loc[:,column].notnull()] = stripped

    target = list(removed_merged.loc[:,"reason_non_competiotin"][removed_merged.loc[:,"reason_non_competiotin"].notnull()])
    removed_merged.loc[:,"reason_non_competiotin"][removed_merged.loc[:,"reason_non_competiotin"].notnull()] = list([("\'"+str(i)+"\'") for i in target])
    return removed_merged

def company_id(removed_merged):
    removed_merged.loc[:,"法人番号"] = list(removed_merged.loc[:,"法人番号"].replace("-",""))
    return removed_merged

#列名を英語に変更する
def alter_col_names(removed_merged):
    export_df = removed_merged[['単位', '契約締結日', '契約金額(円)', '数量', '法人番号',
                                '物品役務等の名称', 'contractor', 'JFY','initial_cost',
                                'R&D', 'unit_price', 'MDA', 'competition', 'reason_non_competiotin']]

    export_df.columns = ['unit', 'contract_date', 'contract_amount', 'quantity', 'company_id',
                                'description', 'contractor', 'JFY','initial_cost',
                                'R&D', 'unit_price', 'FMS', 'competition', 'reason_non_competiotin']
return removed_merged
