# 取得したレース結果に、日付を付加したい
import csv

# CSVフォルダ
READ_FOLDER = "data/race_id/"
# 対象年度
YEAR = "2008"

# 各開催日の開催場数を一次元配列に取る
jousuu = []
with open(READ_FOLDER + str(YEAR) + ".csv") as f:
    for i in f:
        jousuu.append(round(len(i)//13/12))
print(jousuu)

# 
