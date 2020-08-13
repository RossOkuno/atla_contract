import unicodedata
import pandas as pd
import os
import re
from datetime import datetime
import unicodedata

# Incorporate 3columns and make a "contracotor" colunm
def add_contractor_column(df):
    #create contractor column
    name1 = "契約相手方の名称"
    name2 = "契約の相手方の商号又は名称及び住所"
    name3 = "契約相手方の商号又は名称及び住所"
    df["contractor"] = df[name1]
    df["contractor"][df["contractor"].isnull()] = df[name2][df["contractor"].isnull()]
    df["contractor"][df["contractor"].isnull()] = df[name3][df["contractor"].isnull()]

    contractor_list = []
    for i in df["contractor"]:
        text = re.search('\S+',str(i)).group()
        contractor_list.append(text)
    df["contractor"] = contractor_list
    return df

def remove_null_no_amount(df):
    df = df.dropna(subset=['契約金額(円)'])
    return df

#列名を正規化
def normalize_columns(df):
    exclude_cols =  ['予定価格(円)', '再就職の役員の数', '契約金額(円)','契約締結日', '応札・応募者数', '数量', '落札率', "法人番号"]
    target_cols = [col for col in df.columns if col not in exclude_cols]
    for i in target_cols:
        try:
            df[i] = df[i].str.normalize("NFKC")
        except:
            print("skipped", i)
    return df

def make_JFY_column(date) :
    #return:Fiscal year (month, day not included) input:date (timestamp) 
    end_month_fy = 3
    if date.month <= end_month_fy:
        fy = date.year - 1 
        return  fy
    else:
        fy = date.year
        return fy 

# ADD JFY column 
def add_jfy(df):
    JFY = []
    JFY = df['契約締結日'].apply(make_JFY_column)
    df["JFY"] = JFY
    return df

# create Initial_cost column to understand if the contract is for initial (development) not production
def add_initial_cost(df):
    df["initial_cost"] = ""
    target_word = "初度費"
    df["initial_cost"] = [target_word in i for i in df["物品役務等の名称"]]
    return df

# create R%D column
def add_randd(df):
    list_items = list(df["物品役務等の名称"])
    list_RandD = []
    target_word = "調査研究"
    target_word2 = "研究試作"
    for i in range(len(df)):
        item = str(list_items[i])
        if target_word in item:
            list_RandD.append(True)
        elif target_word2 in item:
            list_RandD.append(True)    
        else:
            list_RandD.append(False)
    df["R&D"] = list_RandD
    return df
            
# create unit_price column
def add_unitprice(df):
    df["unit_price"] = round(df["契約金額(円)"] / df["数量"])
    return df

# create MDA column
def add_MDA(df):
    target_text = "(MDA)"
    list1 = list(df["随意契約によることとした会計法令の根拠条文及び理由"])
    list2 = list(df["随意契約によることとした会計法令の根拠条文及び理由(企画競争又は公募)"])
    list_MDA = []
    for i in range(len(df)):
        text = list1[i]
        text2 = list2[i]
        if (target_text in str(text)) == True:
            list_MDA.append(True)

        elif (target_text in str(text2)) == True:
            list_MDA.append(True)

        else:
            list_MDA.append(False)

    df["MDA"] = list_MDA
    return df

# "competition"と"reason_non_competiotin"の列を追加
def add_competition(df):
    df["competition"] = df["一般競争入札・指名競争入札の別(総合評価の実施)"].notnull()
    df["reason_non_competiotin"] = df["随意契約によることとした会計法令の根拠条文及び理由"]
    df["reason_non_competiotin"][df["reason_non_competiotin"].isnull()] = df["随意契約によることとした会計法令の根拠条文及び理由(企画競争又は公募)"][df["reason_non_competiotin"].isnull()]
    return df

# Remove balanks from 物品役務等の名称 and contractor
def remove_blankrows(df):
    strip_target = ["物品役務等の名称", "contractor", "reason_non_competiotin"]
    for column in strip_target:
        target = list(df.loc[:,column][df.loc[:,column].notnull()])
        stripped = [i.strip() for i in target]
        stripped = [i.replace("\r\n", "") for i in stripped]
        stripped = [i.replace("\n", "") for i in stripped]
        stripped = [i.replace("\'", "") for i in stripped]
        stripped = [i.replace("\"", "") for i in stripped]
        df.loc[:,column][df.loc[:,column].notnull()] = stripped

    target = list(df.loc[:,"reason_non_competiotin"][df.loc[:,"reason_non_competiotin"].notnull()])
    df.loc[:,"reason_non_competiotin"][df.loc[:,"reason_non_competiotin"].notnull()] = list([("\'"+str(i)+"\'") for i in target])
    return df

def company_id(df):
    df.loc[:,"法人番号"] = list(df.loc[:,"法人番号"].replace("-",""))
    return df

#列名を英語に変更する
def alter_col_names(df):
    export_df = df[['単位', '契約締結日', '契約金額(円)', '数量', '法人番号', 
                    '物品役務等の名称', 'contractor', 'JFY','initial_cost', 
                    'R&D', 'unit_price', 'MDA', 'competition', 'reason_non_competiotin']]

    export_df.columns = ['unit', 'contract_date', 'contract_amount', 'quantity', 'company_id',
                        'description', 'contractor', 'JFY','initial_cost','R&D', 'unit_price', 
                        'FMS', 'competition', 'reason_non_competiotin']
    return df

def tmp(df):
    df = add_contractor_column(df)
    df = remove_null_no_amount(df)
    df = normalize_columns(df)
    df = add_jfy(df)
    df = add_initial_cost(df)
    df = add_randd(df)
    df = add_unitprice(df)
    df = add_MDA(df)
    df = add_contractor_column(df)
    df = add_competition(df)
    df = remove_blankrows(df)
    df = company_id(df)
    df = alter_col_names(df)
    return df

if __name__ == "__main__":
    main()