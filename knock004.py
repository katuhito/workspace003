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


"""文字列型の変数を処理できるように整形する"""
#機械学習を行う際に、会員区分や性別などの文字列データにはどのように対応すれば良いか？
#性別などのカテゴリー関連のデータをカテゴリカル変数と呼ぶ。これらの変数も機械学習を行ううえで重要な変数となってくる。これをダミー変数化という。
#ダミー変数化=>

#目的の予測に関するデータに絞り込む。
#ここでは、1ヶ月前の利用回数count_1,カテゴリ変数であるcampaign_name,class_name,gender,定期利用のフラグであるroutine_flg,在籍期間のperiodを説明変数に使用し、目的変数は、退会フラグとなるis_deletedとなる。
#教師あり学習の分類を行う。分類は回帰と違い、退会か継続かの目的変数に用いる。
target_col = ["campaign_name", "class_name", "gender", "count_1", "routine_flg", "period", "is_deleted"]
predict_data = predict_data[target_col]
predict_data.head()

#データを絞り込んだら、カテゴリカル変数を用いてダミー変数を作成する
predict_data = pd.get_dummies(predict_data)
predict_data.head()

#pandasは、get_dummiesを使用すると一括でダミー変数化が可能である。文字列データを列に格納すると、簡単にダミー変数化ができる。
#ダミー変数：例えば男性と女性を表現するうえで、0が男性で1が女性であるとき、女性(gender_F)に1が格納されていれば女性で、0であれば男性であると理解できるので、ここでわざわざ男性列(gender_M)を表現する必要はない。会員区分なども同じである。(データの重複を避ける)
#ここで、campaign_name_通常,campaign_name_ナイト,gender_M列を削除する。
del predict_data["campaign_name_通常"]
del predict_data["class_name_ナイト"]
del predict_data["gender_M"]
predict_data.head()


"""決定木を用いて退会予測モデルを作成してみる"""
#退会予測モデルの構築
#決定木アルゴリズムを用いる。=>機械学習によるモデル構築
from sklearn.tree import DecisionTreeClassifier
import sklearn.model_selection

exit = predict_data.loc[predict_data["is_deleted"]==1]
conti = predict_data.loc[predict_data["is_deleted"]==0].sample(len(exit))

X = pd.concat([exit, conti], ignore_index=True)
y = X["is_deleted"]
del X["is_deleted"]
X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y)

model = DecisionTreeClassifier(random_state=0)
model.fit(X_train, y_train)
y_test_pred = model.predict(X_test)
print(y_test_pred)

#会員期間の追加
#実際に正解との比較を行うために、実際の値y_testと一緒にデータフレームに格納しておく
results_test = pd.DataFrame({"y_test":y_test, "y_pred":y_test_pred})
results_test.head()


"""予測モデルの評価して、モデルのチューニングを行う"""
#先のresults_testデータを集計して正解率を出す。正解しているデータは、results_testデータのy_test列とy_pred列が一致しているデータの件数になる。その件数を、全体のデータ件数で割れば正解率が出る。
correct = len(results_test.loc[results_test["y_test"]==results_test["y_pred"]])
data_count = len(results_test)
score_test = correct / data_count
print(score_test)

#機械学習の目的はあくまでも未知のデータへの適合であり、学習用データで予測して精度と評価用データで予測した精度の差が小さいのが理想である。
#score関数を用いて精度を算出する。
print(model.score(X_test, y_test))
print(model.score(X_train, y_train))

#決定木モデルの簡易化
#学習用データが評価用データより高い精度を出す場合には、過学習傾向にあるといえる。その場合は、変数の見直しや、モデルのパラメータを変更したりするなどで理想的なモデルに近づける。
#モデルのパラメータをチューニングする
#決定木は、最もキレイに0と1を分割できる説明変数及びその件を探す作業を、木構造上に派生させていく手法である。
#分割していく木構造の深さを浅くしてしまえばモデルは簡易化できる。
X = pd.concat([exit, conti], ignore_index=True)
y = X["is_deleted"]
del X["is_deleted"]
X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y)

model = DecisionTreeClassifier(random_state=0, max_depth=5)
model.fit(X_train, y_train)
print(model.score(X_test, y_test))
print(model.score(X_train, y_train))


"""モデルに寄与している変数を確認する"""
#モデルに寄与している変数の確認
importance = pd.DataFrame({"feature_names": X.columns, "coefficient": model.feature_importances_})
importance


"""顧客の退会を予測"""
#入力はモデル作成時に使用した説明変数となる。
#1ヶ月前の利用回数3回、定期利用者、在籍期間10,キャンペーン区分は入会費無料、会員区分はオールタイム、性別は男性で作成で変数を定義していく。
count_1 = 3
routing_flg = 1
period = 10
campaign_name = "入会費無料"
class_name = "オールタイム"
gender = "M"

#点数の定義後、データ加工を行う。カテゴリカル変数を用いる。
if campaign_name == "入会費半額":
    campaign_name_list = [1, 0]
elif campaign_name == "入会費無料":
    campaign_name_list = [0, 1]
elif campaign_name == "通常":
    campaign_name_list = [0, 0]
if class_name == "オールタイム":
    class_name_list = [1, 0]
elif class_name == "デイタイム":
    class_name_list = [0, 1]
elif class_name == "ナイト":
    class_name_list = [0, 0]
if gender == "F":
    gender_list = [1]
elif gender == "M":
    gender_list = [0]

input_data = [count_1, routing_flg, period]
input_data.extend(campaign_name_list)
input_data.extend(class_name_list)
input_data.extend(gender_list)

print(model.predict([input_data]))
print(model.predict_proba([input_data]))




















