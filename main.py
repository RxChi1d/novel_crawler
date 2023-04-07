from selenium import webdriver
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import sleep
import random
from multiprocessing import Pool

# 設定Edge的options
edge_options = webdriver.EdgeOptions()
edge_options.add_argument("-minimized")
edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])

# 使用Edge瀏覽器，並傳入options
driver = webdriver.Edge(options=edge_options)

url = 'https://www.banxia.co/203_203989/'
# 前往目標網址
driver.get(url)

# 取得網頁內容
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')
chapter_list = soup.select('div.book-list a')

# 找到每一章節的連結
chapter_dict = {}
for i, chapter in enumerate(chapter_list):
    title = chapter.get('title')
    href = chapter.get('href')

    if href and href.startswith('/203_203989/'):
        chapter_dict[i+1] = {'title': title,
                             'url': 'https://www.banxia.co' + href}


def scrape_chapter(chapter_data):
    title = chapter_data['title']
    url = chapter_data['url']

    driver.execute_script(f"window.location = '{url}'")
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    content = soup.find(id='nr1').text.replace('&nbsp;&nbsp;&nbsp;&nbsp;', '')

    # 儲存成txt檔案
    with open(f'chapter/{title}.txt', 'w', encoding='utf-8') as f:
        f.write(title + '\n\n')
        f.write(content)

    # Sleep
    delay = random.uniform(10, 30)
    sleep(delay)
    return title


if __name__ == '__main__':
    # 使用multiprocessing.Pool進行多進程，不建議設定太多以免被網站ban
    pool = Pool(processes=4)

    start = 1  # 開始章節
    chapter_data_list = [chapter_dict[i]
                         for i in range(start, len(chapter_dict)+1)]

    results = []
    for result in tqdm(pool.imap_unordered(scrape_chapter, chapter_data_list), total=len(chapter_dict)-start+1):
        results.append(result)

    pool.close()
    pool.join()
