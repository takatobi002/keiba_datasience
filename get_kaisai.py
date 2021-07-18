import bs4
import traceback
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv
 
# ドライバーのフルパス
# CHROMEDRIVER = "/mnt/c/Program Files/Google/chromedriver_win32/chromedriver.exe"

# 改ページ（最大）
PAGE_MAX = 120
# 遷移間隔（秒）
INTERVAL_TIME = 3

# 対象年度
# YEAR =[i for i in range(2011, 2021)]
YEAR = [2021]
print(YEAR)

# CSV保存先
CSV_FOLDER = "data/kaisai/"
 
# ドライバー準備
def get_driver():
    # ヘッドレスモードでブラウザを起動
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
 
    # ブラウザーを起動which 
    # driver = webdriver.Chrome(CHROMEDRIVER, options=options)
    driver = webdriver.Chrome(options=options)

 
    return driver
 
 
# 対象ページのソース取得
def get_source_from_page(driver, page):
    try:
        # ターゲット
        driver.get(page)
        driver.implicitly_wait(10)  # 見つからないときは、10秒まで待つ
        page_source = driver.page_source
 
        return page_source

    except Exception:
        print("Exception\n" + traceback.format_exc())
        return None
 
 
# ソースからスクレイピングする
def get_data_from_source(src):
    # スクレイピングする
    soup = bs4.BeautifulSoup(src, features='lxml')
 
    try:
        info = []
        table = soup.find(class_="Calendar_Table")
 
        if table:
            elems = table.find_all("td", class_="RaceCellBox")
 
            for elem in elems:
                a_tag = elem.find("a")
 
                if a_tag:
                    href = a_tag.attrs['href']
                    match = re.findall("\/top\/race_list.html\?kaisai_date=(.*)$", href)
 
                    if len(match) > 0:
                        item_id = match[0]
                        info.append(item_id)
 
        return info
 
    except Exception:
        print("Exception\n" + traceback.format_exc())
        return None
 
 
if __name__ == "__main__":
 
    # ブラウザのdriver取得
    driver = get_driver()
 
    # ページカウンター制御
    page_counter = 0
 
    for year in YEAR:
        for month in range(1, 13):
 
            page_counter = page_counter + 1
 
            # 対象ページURL
            page = "https://race.netkeiba.com/top/calendar.html?year=" + str(year) + "&month=" + str(month)
            # print(page)
 
            # ページのソース取得
            source = get_source_from_page(driver, page)
 
            # ソースからデータ抽出
            data = get_data_from_source(source)
 
            # データ保存
            with open(CSV_FOLDER + str(year) + ".csv", 'a+') as f:
                writer = csv.writer(f)
                writer.writerow(data)

            print(data)
 
            # 間隔を設ける(秒単位）
            time.sleep(INTERVAL_TIME)
 
            # 改ページ処理を抜ける
            if page_counter == PAGE_MAX:
                break
 
        # 改ページ処理を抜ける
        if page_counter == PAGE_MAX:
            break
    # 閉じる
    driver.quit()