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


"""継続顧客のデータを作成する"""
#継続顧客は、退会月があるわけではないので、どの年月のデータを作成しても良い。
#データを継続顧客に絞り込んだ後、uselogデータに結合して作成する。

conti_customer = customer.loc[customer["is_deleted"]==0]
conti_uselog = pd.merge(uselog, conti_customer, on=["customer_id"], how="left")
print(len(conti_uselog))
conti_uselog = conti_uselog.dropna(subset=["name"])
print(len(conti_uselog))

#データをシャッフルして、重複を削除する。
conti_uselog = conti_uselog.sample(frac=1).reset_index(drop=True)
conti_uselog = conti_uselog.drop_duplicates(subset="customer_id")
print(len(conti_uselog))
conti_uselog.head()

#継続顧客と退会顧客の結合
predict_data = pd.concat([conti_uselog, exit_uselog], ignore_index=True)
print(len(predict_data))
predict_data.head()

"""予測する月の在籍期間を作成"""
#在籍期間のデータを変数として扱う。
#在籍期間の列を追加する。
predict_data["period"] = 0
predict_data["now_date"] = pd.to_datetime(predict_data["年月"], format="%Y%m")
predict_data["start_date"] = pd.to_datetime(predict_data["start_date"])
for i in range(len(predict_data)):
    delta = relativedelta(predict_data["now_date"][i], predict_data["start_date"][i])
    predict_data["period"][i] = int(delta.years*12 + delta.months)
predict_data.head()

"""欠損値の除去"""
#機械学習は欠損値があると対応できないので、欠損値は除外するか補間を行う必要がある。
#ここでは、欠損値が含まれているデータの除去を行う。
#最初に、欠損地の数を把握する。
predict_data.isna().sum()

#欠損値があるend_dateとexit_date,count_1のうち、end_date,exit_dateは退会顧客しか値を持っておらず、継続顧客は欠損値となる。そこで、count_1が欠損しているデータだけ除外する。
#dropnaのsubsetで列を指定することで、特定の列が欠損しているデータの除外ができる。
#欠損値は、end_date,exit_dateのみが欠損値を持つことが確認できる。
predict_data = predict_data.dropna(subset=["count_1"])
predict_data.isna().sum()










