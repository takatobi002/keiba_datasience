import bs4
import traceback
import re
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
 
 
# ドライバーのフルパス
CHROMEDRIVER = "/home/inaho/Documents/chromedriver_linux64/chromedriver"

# 改ページ（最大）
PAGE_MAX = 1
# 遷移間隔（秒）
INTERVAL_TIME = 3

# CSVフォルダ
READ_FOLDER = "data/race_id/"
RIGHT_FOLDER = "data/race_result/"
# 対象年度
YEAR = "2008"

# ドライバー準備
def get_driver():
    # ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument('--headless')
 
    # ブラウザーを起動
    driver = webdriver.Chrome(CHROMEDRIVER, options=options)
 
    return driver

# 対象ページのソース取得
def get_source_from_page(driver, page):
    try:
        # ターゲット
        driver.get(page)
        # class="RaceList_NameBox"の要素が見つかるまで10秒は待つ
        target_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "RaceList_NameBox"))
        )
 
        if target_elem:
            page_source = driver.page_source
            return page_source
        else:
            return None
 
    except Exception:
        print("Exception\n" + traceback.format_exc())
        return None
 
# ソースからスクレイピングする
def get_data_from_source(src):
 
    try:
        # スクレイピングする
        soup = bs4.BeautifulSoup(src, features='lxml')
 
        info = {}
        info["race_info"] = None
        info["race_order"] = None
        info["payout"] = None
        info["rap_pace"] = None
 
        # レース情報取得
        info["race_info"] = get_race_info(soup)
        # 全着順取得
        info["race_order"] = get_order(soup)
        # 払い戻し取得
        info["payout"] = get_payout(soup)
        # ラップタイム取得
        info["rap_pace"] = get_rap_pace(soup)
 
        return info
 
    except Exception:
        print("Exception\n" + traceback.format_exc())
        return None

# レース情報の抽出
def get_race_info(soup):
 
    result = {}
    result["no"] = None
    result["name"] = None
    result["time"] = None
    result["kind"] = None
    result["weather"] = None
    result["state"] = None
    result["course"] = None
    result["etc_1"] = None
    result["etc_2"] = None
    result["etc_3"] = None
    result["etc_4"] = None
    result["etc_5"] = None
    result["etc_6"] = None
    result["etc_7"] = None
    result["etc_8"] = None
 
    elem_base = soup.find(class_="RaceList_NameBox")
    if elem_base:
        tmp_elem = elem_base.find(class_="RaceNum")
        if tmp_elem:
            tmp_data = tmp_elem.text
            result["no"] = my_trim(tmp_data)
 
        tmp_elem = elem_base.find(class_="RaceName")
        if tmp_elem:
            tmp_data = tmp_elem.text
            result["name"] = my_trim(tmp_data)
 
        tmp_elem = elem_base.find(class_="RaceData01")
        if tmp_elem:
            tmp_data = tmp_elem.text
            tmp_data_list = tmp_data.split("/")
            if len(tmp_data_list) >= 4:
                result["time"] = my_trim(tmp_data_list[0])
                result["kind"] = my_trim(tmp_data_list[1])
                result["weather"] = my_trim(tmp_data_list[2])
                result["state"] = my_trim(tmp_data_list[3])
 
        tmp_elem = elem_base.find(class_="RaceData02")
        if tmp_elem:
            elems = tmp_elem.find_all("span")
            if len(elems) >=9:
                result["course"] = my_trim(elems[1].text)
                result["etc_1"] = my_trim(elems[0].text)
                result["etc_2"] = my_trim(elems[2].text)
                result["etc_3"] = my_trim(elems[3].text)
                result["etc_4"] = my_trim(elems[4].text)
                result["etc_5"] = my_trim(elems[5].text)
                result["etc_6"] = my_trim(elems[6].text)
                result["etc_7"] = my_trim(elems[7].text)
                result["etc_8"] = my_trim(elems[8].text)
 
    return result
  
# 全着順の抽出
def get_order(soup):
 
    result = []
 
    elem_base = soup.find(id="All_Result_Table")
    if elem_base:
        tr_elems = elem_base.find_all("tr", class_="HorseList")
 
        for tr_elem in tr_elems:
            tmp = {}
            td_elems = tr_elem.find_all("td")
 
            if len(td_elems)==15:
                tmp["rank"] = my_trim(td_elems[0].text)
                tmp["waku"] = my_trim(td_elems[1].text)
                tmp["umaban"] = my_trim(td_elems[2].text)
                tmp["horse_name"] = my_trim(td_elems[3].text)
                tmp["horse_age"] = my_trim(td_elems[4].text)
                tmp["jockey_weight"] = my_trim(td_elems[5].text)
                tmp["jockey_name"] = my_trim(td_elems[6].text)
                tmp["time_1"] = my_trim(td_elems[7].text)
                tmp["time_2"] = my_trim(td_elems[8].text)
                tmp["odds_1"] = my_trim(td_elems[9].text)
                tmp["odds_2"] = my_trim(td_elems[10].text)
                tmp["time_3"] = my_trim(td_elems[11].text)
                tmp["passage_rate"] = my_trim(td_elems[12].text)
                tmp["trainer_name"] = my_trim(td_elems[13].text)
                tmp["horse_weight"] = my_trim(td_elems[14].text)
 
                # 馬ID
                a_tag = td_elems[3].find("a")
                if a_tag:
                    href = a_tag.attrs['href']
                    match = re.findall("\/horse\/(.*)$", href)
                    if len(match) > 0:
                        tmp_id = match[0]
                        tmp["horse_id"] = tmp_id
 
                # 騎手ID
                a_tag = td_elems[6].find("a")
                if a_tag:
                    href = a_tag.attrs['href']
                    match = re.findall("\/jockey\/(.*)\/", href)
                    if len(match) > 0:
                        tmp_id = match[0]
                        tmp["jockey_id"] = tmp_id
 
                # 厩舎ID
                a_tag = td_elems[13].find("a")
                if a_tag:
                    href = a_tag.attrs['href']
                    match = re.findall("\/trainer\/(.*)\/", href)
                    if len(match) > 0:
                        tmp_id = match[0]
                        tmp["trainer_id"] = tmp_id
 
            result.append(tmp)
 
    return result
 
# 払い戻し取得
def get_payout(soup):
 
    result = {}
 
    elem_base = soup.find(class_="FullWrap")
    if elem_base:
        tr_elems = elem_base.find_all("tr")
 
        for tr_elem in tr_elems:
 
            row_list = []
 
            class_name = tr_elem.attrs["class"]
            # class名を小文字にに変換
            class_name = class_name[0].lower()
 
            td_elems = tr_elem.find_all("td")
            if len(td_elems) == 3:
 
                # Ninkiのspan数が行数と判断可能
                span_elems = td_elems[2].find_all("span")
                count = len(span_elems)
                # Payoutのテキストをbrで分割してできるデータ数とcountが同じ
                # ただ、分割は「円」で行う
                payout_text = td_elems[1].text
                payout_text_list = payout_text.split("円")
 
                if class_name=="tansho" or class_name=="fukusho":
                    # Resultのdiv数がcountの3倍
                    target_elems = td_elems[0].find_all("div")
                else:
                    # Resultのul数がcountと同じ
                    target_elems = td_elems[0].find_all("ul")
 
                for i in range(count):
                    tmp = {}
                    tmp["payout"] = my_trim(payout_text_list[i]) + "円"
                    tmp["ninki"] = my_trim(span_elems[i].text)
 
                    target_str = ""
                    if class_name == "tansho" or class_name == "fukusho":
                        target_str = my_trim(target_elems[i*3].text)
                    else:
                        li_elems = target_elems[i].find_all("li")
                        for li_elem in li_elems:
                            tmp_str = my_trim(li_elem.text)
                            if tmp_str:
                                target_str = target_str + "-" + tmp_str
                        # 先頭の文字を削除
                        target_str = target_str.lstrip("-")
 
                    tmp["result"] = target_str
 
                    row_list.append(tmp)
 
            result[class_name] = row_list
 
    return result
 
# ラップタイム取得
def get_rap_pace(soup):
 
    result = []
    row_list = []
 
    elem_base = soup.find(class_="Race_HaronTime")
    if elem_base:
        tr_elems = elem_base.find_all("tr")
 
        counter = 0
        for tr_elem in tr_elems:
 
            col_list = []
            if  counter == 0:
                target_elems = tr_elem.find_all("th")
            else:
                target_elems = tr_elem.find_all("td")
 
            for target_elem in target_elems:
                tmp_str = my_trim(target_elem.text)
                col_list.append(tmp_str)
 
            row_list.append(col_list)
 
            counter = counter + 1

        for i in range(len(row_list[0])):
            tmp = {}
            tmp["header"] = row_list[0][i]
            tmp["haron_time_1"] = row_list[1][i]
            tmp["haron_time_2"] = row_list[2][i]
    
            result.append(tmp)
 
    return result

# 数値だけ抽出
def extract_num(val):
    num = None
    if val:
        match = re.findall("\d+\.\d+", val)
        if len(match) > 0:
            num = match[0]
        else:
            num = re.sub("\\D", "", val)
 
    if not num:
        num = 0
 
    return num

def my_trim(text):
    text = text.replace("\n", "")
    return text.strip()
 
# race_idリスト取得
def get_list_id():
    list_id = []
    with open("data/race_id/" + YEAR + ".csv", "r") as f:
        reader = csv.reader(f)
        for day_list_id in reader:
            list_id.append(day_list_id)
    return list_id
 
 
if __name__ == "__main__":
 
    # list_idリスト取得
    list_id = get_list_id()
 
    # ブラウザのdriver取得
    driver = get_driver()
 
    # ページカウンター制御
    page_counter = 0
 
    for day_race_id in list_id:
        print(day_race_id)
        for race_id in day_race_id:
            print(race_id)
            # 対象ページURL
            page = "https://race.netkeiba.com/race/result.html?race_id=" + str(race_id)

            # ページのソース取得
            source = get_source_from_page(driver, page)

            # ソースからデータ抽出
            data = get_data_from_source(source)

            # データ保存
            with open(RIGHT_FOLDER + str(YEAR) + ".csv", 'a+') as f:
                writer = csv.writer(f)
                write_race = []
                for k,v in data.items():
                    # for i in range(4):
                    write_race.append([k,v])
                writer.writerow(write_race)
            # print(write_race)

            # 間隔を設ける(秒単位）
            time.sleep(INTERVAL_TIME)
 
    # 閉じる
    driver.quit()