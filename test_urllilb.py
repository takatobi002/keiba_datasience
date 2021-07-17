#ライブラリ取得
import urllib.request
import lxml.html

#url読み込み
url = "https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=20080105"
# url = "https://race.netkeiba.com/top/race_list.html?kaisai_date=20080105"

html = urllib.request.urlopen(url).read()

# データの読み込み
dom = lxml.html.fromstring(html)
# print(html)
# for elem in dom.xpath('//*[@class="ItemTitle"]'):
#         print(elem.text)
for elem in dom.xpath('//*[@id="RaceTopRace"]'):
        print(elem.text)
