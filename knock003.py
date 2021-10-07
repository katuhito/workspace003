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

#最新顧客データの基礎集計
#最新月のユーザーに飲み絞り込みを行う
#2019年3月に退会、在籍しているユーザーに絞り込む
customer_join["end_date"] = pd.to_datetime(customer_join["end_date"])
costomer_newer = customer_join.loc[(customer_join["end_date"] >= pd.to_datetime("20190331")) | (customer_join["end_date"].isna())]
print(len(customer_newer))
coustomer_newer["end_date"].unique()

#会員区分
customer_newer.groupby("class_name").count()["customer_id"]

#キャンペーン区分
customer_newer.groupby("campaign_name").count()["customer_id"]

#性別毎
customer_newer.groupby("gender").count()["customer_id"]


#利用履歴データを集計
#データ集計に時間的な要素を取り入れる
#月利用回数の平均値、中央値、最大値、最小値と定期的に利用しているかのフラグを作成し、顧客データを追加していく

#顧客毎の月利用回数を集計したデータを作成
uselog["usedate"] = pd.to_datetime(uselog["usedate"])
uselog["年月"] = uselog["usedate"].dt.strftime("%Y%m")
uselog_months = uselog.groupby(["年月","coustomer_id"], as_index=False).count()
uselog_months.rename(columns={"log_id":"count"}, inplace=True)
del uselog_months["usedate"]
uselog_months.head()

#ここから顧客毎に絞り込み、平均値、中央値、最大値、最小値を集計する
#顧客毎の月内の利用回数の集計
uselog_customer = uselog_months.groupby("customer_id").agg(["mean", "median", "max", "min"])["count"]
uselog_customer = uselog_customer.reset_index(drop=False)
uselog_customer.head()

#利用履歴データから定期利用フラグを作成
#定期的にジムを利用しているユーザーを特定
#顧客毎に月／曜日別に集計を行い、最大値が4以上の曜日が1ヶ月でもあったユーザーはフラグ1とする

#最初に顧客毎に月／曜日別に集計を行う
uselog["weekday"] = uselog["usedate"].dt.weekday
uselog_weekday = uselog.groupby(["customer_id", "年月", "weekday"], as_index = False).count()[["customer_id", "年月", "weekday", "log_id"]]
uselog_weekday.rename(columns={"log_id":"count"}, inplace=True)
uselog_weekday.head()

#顧客毎の各月の最大値を取得し、その最大値が4以上の場合にフラグを立てる。
uselog_weekday = uselog_weekday.groupby("customer_id", as_index=False).max()[["customer_id", "count"]]
uselog_weekday["routine_flg"] = 0
uselog_weekday["routine_flg"] = uselog_weekday["routine_flg"].where(uselog_weekday["count"] < 4, 1)
uselog_weekday.head()

#uselog_customer, uselog_weekdayを、customer_joinと結合する
customer_join = pd.merge(customer_join, uselog_customer, on="customer_id", how="left")
customer_join = pd.merge(customer_join, uselog_weekday[["customer_id", "routine_flg"]], on="customer_id", how="left")
customer_join.head()

#欠損値
customer_join.isnull().sum()

#会員期間の計算
#会員期間は、start_dateとend_dateの差になるが、2019年3月までに退会していないユーザーに関しては、end_dateに欠損値が入っているので、差の計算ができない。そのため、2019年4月をend_dateとして会員期間を算出する。
#月単位での集計
from dateutil.relativedelta import relativedelta
customer_join["calc_date"] = customer_join["end_date"]
customer_join["calc_date"] = customer_join["calc_data"].fillna(pd.to_datetime("20190430"))
customer_join["membership_period"] = 0
for i in range(len(cuntomer_join)):
    delta = relativedelta(customer_join["calc_date"].iloc[i], customer_join["start_date"].iloc[i])
    customer_join["membership_period"].iloc[i] = delta.years*12 + delta.months
customer_join.head()

#顧客行動の各種統計量を把握する
customer_join[["mean", "median", "max", "min"]].describe()

#routine_flgを集計
customer_join.groupby("routine_flg").count()["customer_id"]

#会員期間の分布を可視化(ヒストグラム)
import matplotlib.pyplot as plt
%matplotlib inline
plt.hist(customer_join["membership_period"])

#退会ユーザーと継続ユーザーの違いを把握する
#退会ユーザーと継続ユーザーを分けて、describeで比較してみる

#退会ユーザー
customer_end = customer_join.loc[customer_join["is_deleted"]==1]
customer_stay.describe()

#継続ユーザー
customer_stay = customer_join.loc[customer_join["is_deleted"]==0]
customer_stay.describe()

#customer_joinをCSV出力
customer_join.to_csv("customer_join.csv", index=False)















