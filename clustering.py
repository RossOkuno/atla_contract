import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime as dt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def large_clients_finder(data, client_id_col_name, value_col_name, threshold_rate):
    """
    This function returns a list of large clients.
    Parameters
    ----------
    data : Pandas DataFrame consists of at least client name column
            and value (such as sales or consumption) column.
    client_id_col_name : String. The name of client name column.
                        E.g. "customer_id"
    value_col_name : String. The name of value column.
                        E.g. "power_usage"s
    threshold_rate : Float. Percentage large clients account for.
        In 80/20 rule, register 0.8.
    """

    # prepare variables for calculation
    large_clients_consumption = 0
    large_clients = []
    total_consumption = data[value_col_name].sum()
    threshold = total_consumption * threshold_rate

    # sort clients by consumption in descending order
    df = data.groupby(client_id_col_name)[value_col_name].sum().reset_index()
    df = df.sort_values(by=value_col_name, ascending=False)

    # add top clients consumption until the sum of its consumption reaches the thereshold
    for i in range(len(df)):
        if large_clients_consumption <= threshold:
            large_clients_consumption += df.iloc[i][value_col_name]
            large_clients.append(df.iloc[i][client_id_col_name])
        else:
            break

    # print how many large clients account for the threshold and return a list of large clients
    print("Top %d (%.2f%%) clients account for %.2f%% of the total consumption or sales." %
          (len(large_clients), (len(large_clients) / len(df)) * 100,
           (large_clients_consumption / total_consumption) * 100))
    return large_clients


def get_pivoted_df(df, columns, index, values):
    pivoted_df = pd.pivot_table(data=df, columns=columns, index=index, values=values, aggfunc=np.sum).reset_index()
    return pivoted_df


def get_non_null_df(df, total=False):
    null_count = []
    not_null_contractors_index_list = []
    for i in range(df.shape[0]):
        row = df.iloc[i,]
        nulls = row.isnull().sum()
        null_count.append(nulls)
        
    for index, value in enumerate(null_count):
        if value == 0:
            not_null_contractors_index_list.append(index)
        else:
            pass
    non_null_df = df.loc[not_null_contractors_index_list,:]
    
    if total==True:
        non_null_df["total"] = non_null_df.sum(axis=1)
    else:
        pass
    return non_null_df
    
    
def get_starnderdized_df(df, values_cols, plot=False):
    """
    Required libarary
    -from sklearn.preprocessing import StandardScaler
    """
    df = df[values_cols]
    scaler = StandardScaler()
    # Apply StandardScaler with transposed dataframe
    df2_std = scaler.fit_transform(df.T) 
    # Return the dataframe to normal shape with transposion
    df_std = pd.DataFrame(df2_std).T
    
    df_std.columns = values_cols
    
    if plot:
        df_std.T.plot(color='blue', alpha=0.05, legend=False)
    else:
        pass
    return df_std

def get_distortions_elbow_method(df, num_cluster, plot=True, random_state=1234):
    """
    Required libarary
    -from sklearn.cluster import KMeans
    """
    distortions = []

    for i  in range(1, num_cluster):                # 1~15クラスタまで計算 
        km = KMeans(n_clusters=i, random_state=random_state)
        km.fit(df)                       # クラスタリングの計算を実行
        distortions.append(km.inertia_)   # km.fitするとkm.inertia_が得られる

    if plot:
        plt.plot(range(1,15),distortions,marker='o')
        plt.xlabel('Number of clusters')
        plt.ylabel('Distortion')
        plt.savefig('elbow_cont_amount.png')
        plt.show()
    
    return distortions

def get_clustered_df(df, num_clusters,  random_state=1234):
    # モデルを初期化
    km =KMeans(n_clusters=num_clusters, random_state=random_state)
    # 学習は教師あり学習と同じように　model.fit(data)で実行します
    km.fit(df)
    # ラベルを付与する場合も教師あり学習同様に model.predict(data)で実行します
    cluster_labels = km.predict(df)
    df["cluster_labels"] = cluster_labels
    
    return df

def plot_cluters(df, values_cols, n_clusters):
    print(pd.pivot_table(data=df, index="cluster_labels", values=values_cols, aggfunc="count").reset_index())
    for i in range(n_clusters):
        df[df["cluster_labels"] == i][values_cols].T.plot(color='blue', alpha=0.05, legend=False)
#             plt.savefig(str(i)+'_small_elbow.png')

def add_removed_cols(df, non_null_df, cols):
    df = df.copy()
    for i in cols:
        df[i] = list(non_null_df[i])
    return df