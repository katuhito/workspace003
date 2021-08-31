"""小売店のデータでデータ加工"""
#データを読み込む
import pandas as pd
#uriage.csvの読み込み
uriage_data = pd.read_csv('./data002/uriage.csv')
uriage_data.head()

#kokyaku_daicho.xlsxの読み込み
kokyaku_data = pd.read_excel('./data002/kokyaku_daicho.xlsx')
kokyaku_data.head()

#データの揺れを確認
uriage_data['item_name'].head()
uriage_data['item_price'].head()

#データの揺れがあるままに集計する
#売り上げ履歴からの商品毎の月売上合計を集計する
uriage_data['purchase_date'] = pd.to_datetime(uriage_data['purchase_date'])
uriage_data['purchase_month'] = uriage_data['purchase_date'].dt.strftime("%Y%m")
res = uriage_data.pivot_table(index="purchase_month", columns="item_name", aggfunc="size", fill_value=0)
res

# 横軸に「item_price」を設定して集計
res = uriage_data.pivot_table(index="purchase_month", columns="item_name", values="item_price", aggfunc="sum", fill_value=0)
res

#商品名の揺れを補正する
#現状の把握　商品名のユニーク数確認
#売り上げ履歴のitem_nameの重複を除外したユニークなデータ件数を確認する
print(len(pd.unique(uriage_data.item_name)))

#データの揺れを解消していく
uriage_data['item_name'] = uriage_data['item_name'].str.upper()
uriage_data['item_name'] = uriage_data['item_name'].str.replace("　", "")
uriage_data['item_name'] = uriage_data['item_name'].str.replace(" ", "")
uriage_data.sort_values(by=['item_name'], ascending=True)

#商品名の補正結果検証
print(pd.unique(uriage_data['item_name']))
print(len(pd.unique(uriage_data['item_name'])))


#金額欠損値の補完
#データ全体から、欠損値が含まれているかどうか確認する
uriage_data.isnull().any(axis=0)

#金額の欠損値を補完する
flg_is_null = uriage_data['item_price'].isnull()
for trg in list(uriage_data.loc[flg_is_null, 'item_name'].unique()):
    price = uriage_data.loc[(~flg_is_null) & (uriage_data['item_name']==trg), 'item_price'].max()
    uriage_data['item_price'].loc[(flg_is_null) & (uriage_data['item_name']==trg)] = price
uriage_data.head()

#欠損値チェック結果(補完後)
uriage_data.isnull().any(axis=0)

#欠損値チェック結果
for trg in list(uriage_data['item_name'].sort_values().unique()):
    print(trg + "の最大額：" + str(uriage_data.loc[uriage_data['item_name']==trg]['item_price'].max()) + "の最小額：" + str(uriage_data.loc[uriage_data['item_name']==trg]['item_price'].min(skipna=False)))


#顧客台帳の顧客名の揺れを補正
#データの確認
kokyaku_data['顧客名'].head()

#売り上げ履歴の顧客名
uriage_data['customer_name'].head()

#顧客台帳の顧客名に対してスペースの除去を行う
kokyaku_data["顧客名"] = kokyaku_data["顧客名"].str.replace("　", "")
kokyaku_data["顧客名"] = kokyaku_data["顧客名"].str.replace(" ", "")
kokyaku_data["顧客名"].head()

#日付の揺れを補正する
#日付を統一フォーマットに補正していく
#数値となっている箇所の特定
flg_is_serial = kokyaku_data["登録日"].astype('str').str.isdigit()
flg_is_serial.sum()

#数値で取り込まれている登録日を補正していく
#数値から日付に変換
fromSerial = pd.to_timedelta(kokyaku_data.loc[flg_is_serial, "登録日"].astype('float'), unit="D") + pd.to_datetime('1900/01/01')
fromSerial

#日付として取り込まれている対象の書式変更結果
fromString = pd.to_datetime(kokyaku_data.loc[~flg_is_serial, "登録日"])
fromString

#数値から日付に補正したデータと、書式を変更したデータを結合してデータを更新する
kokyaku_data["登録日"] = pd.concat([fromSerial, fromString])
kokyaku_data

#登録月の集計結果
kokyaku_data["登録年月"] = kokyaku_data["登録日"].dt.strftime("%Y%m")
rslt = kokyaku_data.groupby("登録年月").count()["顧客名"]
print(rslt)
print(len(kokyaku_data))

#数値項目の有無
#登録日列に数値データが残っていないか確認する
flg_is_serial = kokyaku_data["登録日"].astype('str').str.isdigit()
flg_is_serial.sum()



















