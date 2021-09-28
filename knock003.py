#必要なデータを読み込む(ジムの利用履歴データ)
import pandas as pd
uselog = pd.read_csv('./data003/use_log.csv')
print(len(uselog))
uselog.head()

#2019年3月末時点での会員データ
customer = pd.read_csv('./data003/customer_master.csv')
print(len(customer))
customer.head()

#会員区分データ(オールタイム、デイタイム)
class_master = pd.read_csv('./data003/class_master.csv')
print(len(class_master))
class_master.head()

#キャンペーン区分データ(入会無料等)
campaign_master = pd.read_csv('./data003/campaign_master.csv')
print(len(campaign_master))
campaign_master.head()

#顧客データの整形
#顧客データに、会員区分のclass_masterとキャンペーン区分のcampain_masterを結合する
customer_join = pd.merge(customer, class_master, on="class", how="left")
customer_join = pd.merge(customer_join, campaign_master, on="campaign_id", how="left")
customer_join.head()

#ジョイン後の欠損値の確認
customer_join.isnull().sum()

#顧客データの基礎集計
#会員区分
customer_join.groupby("class_name").count()["customer_id"]
#キャンペーン区分
customer_join.groupby("campaign_name").count()["customer_id"]
#性別区分
customer_join.groupby("gender").count()["customer_id"]
#退会区分
customer_join.groupby("is_deleted").count()["customer_id"]

#入会人数を集計(start_date列)
customer_join["start_date"] = pd.to_datetime(customer_join["start_date"])
customer_start = customer_join.loc[customer_join["start_date"] > pd.to_datetime("20180401")]
print(len(customer_start))






