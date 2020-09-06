import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def get_cleansed_data(df):
    df = df[['法人番号', 'contractor', 'JFY']]
    df['法人番号'][df['法人番号'].notnull()] = df['法人番号'][df['法人番号'].notnull()].astype(int)
    df['法人番号'][df['法人番号'].notnull()] = df['法人番号'][df['法人番号'].notnull()].astype(str)
    return df


def get_all_contractors_names(df):
    non_null_cont = []
    df = df[['法人番号', 'contractor']]
    df = df[~df.duplicated()]
    non_null_cont = list(df['contractor'][df['法人番号'].notnull()])
    df['remove'] = 0
    df['remove'][df['法人番号'].isnull() & df['contractor'].isin(non_null_cont)] = 1
    df = df[df['remove'] != 1]
    df = df[['法人番号', 'contractor']]
    contractors = pd.read_excel('/Users/rairaokuno/atla_contract/data/contractors/contractors.xlsx')
    for i, r in enumerate(contractors['contractor_id']):
        id = r
        former = contractors['former_name'][i]
        current = contractors['current_name'][i]
        if former in list(df['contractor']):
            df['法人番号'][df['contractor'] == former] = id
        else:
            print('pass')
    return df


def get_current_contractors_names(df):
    df = df.dropna(subset=['法人番号']) 
    df = df.sort_values('JFY').reset_index(drop=True)
    df = df[df.duplicated(subset='法人番号', keep='last')==False]
    df = df.reset_index(drop=True)
    df = df[['法人番号', 'contractor']]
    return df


def merge_tables(left_df, right_df):
    df = pd.merge(left_df, right_df, how='left', left_on =["法人番号"], right_on =["法人番号"])
    df.columns = ['contractor_id', 'contractor_name_old', 'contractor_name']
    return df


def run(df, to_excel=False):
    df = pd.read_excel('/Users/rairaokuno/atla_contract/output/merged.xlsx')
    df = get_cleansed_data(df)
    left_df = get_all_contractors_names(df)
    right_df = get_current_contractors_names(df)
    df = merge_tables(left_df, right_df)
    if print:
        df.to_csv('./output/contractors_id.csv', index=False)
    else:
        pass
    return df
