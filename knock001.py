import pandas as pd

#customer_master.csvを読み込む
customer_master = pd.read_csv('./csv001/customer_master.csv')
#customer_masterの先頭5行を表示する
customer_master.head()

#item_master.csvを読み込む
item_master = pd.read_csv('./csv001/item_master.csv')
#item_masterの先頭5行を表示する
item_master.head()

#transaction_1.csv
transaction_1 = pd.read_csv('./csv001/transaction_1.csv')
transaction_1.head()

#transaction_2.csv
transaction_2 = pd.read_csv('./csv001/transaction_2.csv')
transaction_2.head()

#tranceaction_detail_1.csv
transaction_detail_1 = pd.read_csv('./csv001/transaction_detail_1.csv')
transaction_detail_1.head()

#データを結合する(transaction_1, transaction_2)
taransaction_2 = pd.read_csv('./csv001/transaction_3.csv')
transaction = pd.concat([transaction_1, transaction_2], ignore_index=True)
transaction.head()

print(len(transaction_1))
print(len(transaction_2))
print(len(transaction))


#データを結合する(transaction_detail_1, tranceaction_detail_2)
transaction_detail_2 = pd.read_csv('./csv001/transaction_detail_2.csv')
transaction_detail = pd.concat([transaction_detail_1, transaction_detail_2], ignore_index=True)
transaction_detail.head()

#データを結合する(横方向結合)=>売り上げデータのジョイン
join_data = pd.merge(transaction_detail, transaction[["transaction_id", "payment_date", "customer_id"]], on="transaction_id", how="left")
join_data.head()

#データ件数を確認
print(len(transaction_detail))
print(len(transaction))
print(len(join_data))


#マスターデータを結合(ジョイン)=>customer_master, item_master
join_data = pd.merge(join_data, customer_master, on="customer_id", how="left")
join_data = pd.merge(join_data, item_master, on="item_id", how="left")
join_data.head()


#売り上げ列を作成する
join_data["price"] = join_data["quantity"] * join_data["item_price"]
join_data[["quantity", "item_price", "price"]].head()

#作成したデータを検算する
print(join_data["price"].sum())
print(transaction["price"].sum())

#作成したデータを検算する2(ブール演算)
join_data["price"].sum() == transaction["price"].sum()

#各種統計量を把握する1
join_data.isnull().sum()
#各種統計量を把握する2
join_data.describe


#データの範囲（日付）
print(join_data["payment_date"].min())
print(join_data["payment_date"].max())


#月別でデータを集計=>payment_dateのデータ型を確認
join_data.dtypes

#payment_date=>datetime型に変更して、年月列の作成を行う。
join_data["payment_date"] = pd.to_datetime(join_data["payment_date"])
join_data["payment_month"] = join_data["payment_date"].dt.strftime("%Y%m")
join_data[["payment_date", "payment_month"]].head()

#月別売り上げの集計結果
join_data.groupby("payment_month").sum()["price"]


#月別かつ商品別の売り上げの合計値、数量を表示する
join_data.groupby(["payment_month", "item_name"]).sum()[["price", "quantity"]]

#pivot_tableを使用して集計する
pd.pivot_table(join_data, index='item_name', columns='payment_month', values=['price', 'quantity'], aggfunc='sum')

#商品別の売上推移を可視化する=>グラフ用データ作成
graph_data = pd.pivot_table(join_data, index='payment_month', columns='item_name', values='price', aggfunc='sum')
graph_data.head()

#matplotlibを用いて描画
import matplotlib.pyplot as plt
%matplotlib inline
plt.plot(list(graph_data.index), graph_data["PC-A"], label='PC-A')
plt.plot(list(graph_data.index), graph_data["PC-B"], label='PC-B')
plt.plot(list(graph_data.index), graph_data["PC-C"], label='PC-C')
plt.plot(list(graph_data.index), graph_data["PC-D"], label='PC-D')
plt.plot(list(graph_data.index), graph_data["PC-E"], label='PC-E')
plt.legend()
















