"""顧客の退会を予測する"""
#退会してしまう会員が退会する原因を分析する。

#データの読み込み。利用データ整形。
import pandas as pd

customer = pd.read_csv('customer_join.csv')
uselog_months = pd.read_csv('use_log_months.csv')

#機械学習用にデータを加工=>未来を予測
#当月と過去1ヶ月の利用回数を集計したデータを作成
year_months = list(uselog_months["年月"].unique())
uselog = pd.DataFrame()
for i in range(1, len(year_months)):
    tmp = uselog_months.loc[uselog_months["年月"]==year_months[i]]
    tmp.rename(columns={"count":"count_0"}, inplace=True)
    tmp_before = uselog_months.loc[uselog_months["年月"]==year_months[i-1]]
    del tmp_before["年月"]
    tmp_before.rename(columns={"count":"count_1"}, inplace=True)
    tmp = pd.merge(tmp, tmp_before, on="customer_id", how="left")
    uselog = pd.concat([uselog, tmp], ignore_index=True)

uselog.head()


"""退会前月の退会顧客データを作成する"""
#退会前月のデータを作成するのは、退会申請は退会の前月末までに出すことのなっているからである。
#退会した顧客に絞り込んで、end_date列の1ヶ月前の年月を取得し、上記で整形したuselogとcustomer_id,年月をキーにして結合する。
from dateutil.relativedelta import relativedelta

exit_customer = customer.loc[customer["is_deleted"]==1]
exit_customer["exit_date"] = None
exit_customer["end_date"] = pd.to_datetime(exit_customer["end_date"])

for i in range(len(exit_customer)):
    exit_customer["exit_date"].iloc[i] = exit_customer["end_date"].iloc[i] - relativedelta(months=1)

exit_customer["年月"] = exit_customer["exit_date"]
uselog["年月"] = uselog["年月"].astype(str)
exit_uselog = pd.merge(uselog, exit_customer, on=["customer_id", "年月"], how="left")
print(len(uselog))
exit_uselog.head()

#欠損値の除去
exit_uselog = exit_uselog.dropna(subset=["name"])
print(len(exit_uselog))
print(len(exit_uselog["customer_id"].unique()))
exit_uselog.head()





