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



