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



#顧客の行動を予測する
#データを読み込んで確認
import pandas as pd
uselog = pd.read_csv('./data003/use_log.csv')
uselog.isnull().sum()
#欠損値
customer = pd.read_csv('customer_join.csv')
customer.isnull().sum()

"""顧客データをグループ化する"""
#退会しているかどうかではなく、利用履歴に基づいたグループ化を行う
#その場合、あらかじめ決められた正解がないので、教師なし学習のクラスタリングを用いる。
#顧客のグループ化を行う=>customerデータを用いる。
#クラスタリングに用いる変数=>mean, median, max, min,membership_period
#必要な変数に絞り込む
customer_clustering = customer[["mean", "median", "max", "min", "membership_period"]]
customer_clustering.head()

#クラスタリングを行う=>K-means法
#変数間の距離をベースにグループ化を行う。
#あらかじめグルーピングしたい数を指定する必要がある。ここでは4つのグループを指定する
#月内利用回数：[mean,median,max,min]と最大値が47：[membership_period]ではデータの大きさが異なる。その場合、membership_periodに引っ張られてしまうので、標準化が必要になる。
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
customer_clustering_sc = sc.fit_transform(customer_clustering)

kmeans = KMeans(n_clusters=4, random_state=0)
clusters = kmeans.fit(customer_clustering_sc)
customer_clustering["cluster"] = clusters.labels_
print(customer_clustering["cluster"].unique())
customer_clustering.head()

#クラスタリング結果を分析
#グループ毎のデータ件数を表示=>分析を容易にするために列名を変更
customer_clustering.columns = ["月内平均値", "月内中央値", "月内最大値", "月内最小値", "会員期間", "cluster"]
customer_clustering.groupby("cluster").count()

#クラスタリングの結果を分析
#上記の結果では、count()によりデータ件数を取っているので、どの列も同じになっている。
#顧客数の順位は、グループ3,1,0,2となっている。
#ここでグループ毎の平均値を取る
customer_clustering.groupby("cluster").mean()

"""簡易的にクラスタリング結果を可視化する"""
#クラスタリングに使用した変数の数は5つである。
#この5つの変数を2次元助言うにプロットする場合、次元削除を行う。
#次元削除とは、教師なし学習の一種で、情報をなるべく失わないように変数を削除して、新しい軸を作り出すことである。これによって、5つの変数を2つの変数で表現することができ、グラフ化することが可能になる。
#主成分分析：ここでは、次元削除の代表的な手法である主成分分析を用いる。主成分分析を行うには、前出で用いた標準化したデータを用いる。

from sklearn.decomposition import PCA
X = customer_clustering_sc
pca = PCA(n_components=2)
pca.fit(X)
x_pca = pca.transform(X)
pca_df = pd.DataFrame(x_pca)
pca_df["cluster"] = customer_clustering["cluster"]

import matplotlib.pyplot as plt
%matplotlib inline
for i in customer_clustering["cluster"].unique():
    tmp = pca_df.loc[pca_df["cluster"]==i]
    plt.scatter(tmp[0], tmp[1])
    

"""クラスタリング結果を基に退会顧客の傾向を把握する"""
#クラスタリングによって4つのグループに分割されたが、これらのグループの継続顧客と退会顧客の数を調査し、集計する。
#最初に、退会顧客を特定するためにis_deleted列をcustomer_clusteringに追加し、cluster,is_deleted毎に集計を行う。

#グループ毎の退会／継続顧客の集計
customer_clustering = pd.concat([customer_clustering, customer], axis=1)
customer_clustering.groupby(["cluster", "is_deleted"], as_index=False).count()[["cluster", "is_deleted", "customer_id"]]

#定期利用(Flg)しているかどうか
customer_clustering.groupby(["cluster", "routine_flg"], as_index=False).count()[["cluster", "routine_fig", "customer_id"]]



"""翌月の利用回数予測を行うための準備を行う"""
#顧客の過去の行動データから翌月の利用回数を予測するためには、教師あり学習の回帰を用いる。
#ここでは各6ヶ月の利用データを用いて、翌月の利用データを予測する。

#当月が2018年10月で2018年11月の利用回数を予測する。
#予測が目的なので、2018年5月〜10月の6ヶ月の利用データと2018年11月の利用回数を教師データとして学習に使うことにする。
#つまり、これまでの顧客データとは違いある特定の顧客の特定の月のデータを作成する必要がある。

#最初に，uselogデータを用いて年月、顧客毎に集計を行う。
uselog["usedate"] = pd.to_datetime(uselog["usedate"])
uselog["年月"] = uselog["usedate"].dt.strftime("%Y%m")
uselog_months = uselog.groupby(["年月", "customer_id"], as_index=False).count()
uselog_months.rename(columns={"log_id":"count"}, inplace=True)
del uselog_months["usedate"]
uselog_months.head()

#データを整形
year_months = list(uselog_months["年月"].unique())
predict_data = pd.DateFrame()
for i in range(6, len(year_months)):
    tmp = uselog_months.loc[uselog_months["年月"]==year_months[i]]
    tmp.rename(columns={"count":"count_pred"}, inplace=True)
    for j in range(1, 7):
        tmp_before = uselog_months.loc[uselog_months["年月"]==year_months[i-j]]
        del tmp_before["年月"]
        tmp_before.rename(columns={"count":"count_{}".format(j-1)}, inplace=True)
        tmp = pd.merge(tmp, tmp_before, on="customer_id", how="left")
    predict_data = pd.concat([predict_data, tmp], ignore_index=True)
predict_data.head()

#欠損値を含むデータを除去(dropna),indexを初期化
predict_data = predict_data.dropna()
predict_data = predict_data.reset_index(drop=True)
predict_data.head()

#特徴となるデータを付与する
#会員期間を付与する
#顧客データであるcustomerのstart_dateの列を先に作成したpredict_dataに結合する
predict_data = pd.merge(predict_data, customer[["customer_id", "start_date"]], on = "customer_id", how = "left")
predict_data.head()

#年月とstart_dateの差から、会員期間を月単位で作成。
predict_data["now_date"] = pd.to_datetime(predict_data["年月"], format="%Y%m")
predict_data["start_date"] = pd.to_datetime(predict_data["start_date"])

from dateutil.relativedelta import relativedelta
predict_data["period"] = None
for i in range(len(predict_data)):
    delta = relativedelta(predict_data["now_date"][i], predict_data["start_date"][i])
    predict_data["period"][i] = delta.years*12 + delta.months
predict_data.head()

"""来月の予測モデルを作成する。"""
#2018年4月以降に新規に入った顧客に絞ってモデル作成を行う。
#古い顧客は、入店時期のデータが存在せず、利用回数が安定状態にある可能性があるので、今回はデータ対象外として除外する。

#線形回帰モデル=>LinerRegression(scikit-learn)と呼ばれる回帰モデルを使用する。
#データを学習用データと評価用データに分割して、学習を行う。
predict_data = predict_data.loc[predict_data["start_date"] >= pd.to_datetime("20180401")]

from sklearn import linear_model
import sklearn.model_selection

model = linear_model.LinearRegression()
X = predict_data[["count_0","count_1","count_2","count_3","count_4","count_5","period"]]
y = predict_data["count_pred"]
X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y)
model.fit(X_train, y_train)

#学習用データと評価用データに分ける理由
#機械学習はあくまで未知のデータを予測するのが目的となる。そのため、学習に用いたデータに過剰適合してしまうと、未知なデータに対応できなくなり、過学習状態に陥る。なので、学習用データで学習を行い、モデルにとっては未知のデータである評価用データで精度の検証を行う。

#精度の検証=>回帰予測モデル
print(model.score(X_train, y_train))
print(model.score(X_test, y_test))


#モデルに寄与している変数を確認
#説明変数毎に、寄与している変数の係数を出力してみる。
coef = pd.DataFrame({"feature_names":X.columns, "coefficient":model.coef_})
coef

#来月の利用回数を予測する
#2人の顧客の利用データを作成する。1人目は6ヶ月前から1ヶ月毎に7，8，6，4，4，3回来ている顧客で、2人目は6，4，3，3，2，2回来ている顧客で、どちらも8ヶ月の在籍期間の顧客の翌月の来店回数を予測する。
#それぞれの顧客の利用履歴をリストに格納し、データを作成する。
x1 = [3,4,4,6,8,7,8]
x2 = [2,2,3,3,4,6,8]
x_pred = [x1, x2]
#modelを用いて予測を行う。
model.predict(x_pred)

#uselog_monthsデータを出力
uselog_months.to_csv("use_log_months.csv", index=False)


























