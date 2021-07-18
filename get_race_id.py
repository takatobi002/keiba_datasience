import bs4
import traceback
import re
import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# 改ページ（最大）
# PAGE_MAX = 1
# 遷移間隔（秒）
INTERVAL_TIME = 3
 
# 年度
YEAR = "2021"
# 生成するCSVの場所
CSV_FOLDER = "data/race_id/"


# ドライバー準備
def get_driver():
    # ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument('--headless')
 
    # ブラウザーを起動
    driver = webdriver.Chrome(options=options)
    return driver
 
 
# 対象ページのソース取得
def get_source_from_page(driver, page):
    try:
        # ターゲット
        driver.get(page)
        # id="RaceTopRace"の要素が見つかるまで10秒は待つ
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'RaceTopRace')))
        page_source = driver.page_source
        # print(page_source)
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
        elem_base = soup.find(id="RaceTopRace")
 
        if elem_base:
            elems = elem_base.find_all("li", class_="RaceList_DataItem")
            # print(elems[0])
 
            for elem in elems:
                # 最初のaタグ
                a_tag = elem.find("a")
                # print(a_tag)
 
                if a_tag:
                    href = a_tag.attrs['href']
                    print("hrefだよ：" + href)
                    match = re.findall("[0-9]{12}", href)
                    # print(match)
 
                    if len(match) > 0:
                        item_id = match[0]
                        # print(item_id)
                        info.append(item_id)
 
        return info
 
    except Exception:
        print("Exception\n" + traceback.format_exc())
        return None
 
# kaisai_dateリストを取得する
def get_list_id():
    kaisai_date = []
    with open("data/kaisai/" + YEAR + ".csv", "r") as f:
        reader = csv.reader(f)
        for month in reader:
            kaisai_date.append(month)
        print(kaisai_date)
    return kaisai_date

 
if __name__ == "__main__":
 
    # kaisai_dateリスト取得
    list_id = get_list_id()
 
    # ブラウザのdriver取得
    driver = get_driver()
 
    # ページカウンター制御
    page_counter = 0
 
    for month in list_id:
        print(month)
        for kaisai_date in month:
            print(kaisai_date)

            # page_counter =+ 1
    
            # 対象ページURL
            page = "https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=" + str(kaisai_date)

            # ページのソース取得
            source = get_source_from_page(driver, page)
    
            # ソースからデータ抽出
            data = get_data_from_source(source)
    
            # データ保存
            with open(CSV_FOLDER + str(YEAR) + ".csv", 'a+') as f:
                writer = csv.writer(f)
                writer.writerow(data)
            print(data)

            # 間隔を設ける(秒単位）
            time.sleep(INTERVAL_TIME)
    
            # 改ページ処理を抜ける
        #     if page_counter == PAGE_MAX:
        #         break
        # else:
        #     continue
        # break
 
 
    # 閉じる
    driver.quit()