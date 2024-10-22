import requests
from lxml import etree
from pandas import DataFrame
from tqdm import tqdm
import threading


url = input('URL:')

response = requests.get(url)

html = etree.HTML(response.text)

item_urls = html.xpath('//div[@class="__content"]/a/@href')

items = []
lock = threading.Lock()

def downloader(url:str):
    try:
        response = requests.get(url,timeout=10)
        html = etree.HTML(response.text)
        message = html.xpath('//h2[@class="__name"]/text()')
        price = html.xpath('//dl[@class="__jodai"]/dd/text()')
        no = html.xpath('//dl[@class="__no"]/dd/text()')
        origin = html.xpath('//dd[@class="info05"]/text()')
        off = html.xpath('//ul[@class="__list c-breadcrumb"]/li[2]/a/text()')
        # print(origin)
        for key, item in enumerate(price):
            message_list = message[key].replace(' ','').replace('\n','').split('/')
            ans = {
                'name': message_list[0],
                'color': message_list[1],
                'size': message_list[2],
                'no': no[key],
                'price': item,
                'off': off[0],
                'origin': origin[0]
            }
            with lock:
                items.append(ans)
                # print(ans)
    except Exception as e:
        print(e)
        print('Error:', url)



for url in tqdm(item_urls):
    downloader(url)

data = DataFrame(items)
data.to_csv('miki_house.csv', index=False, encoding='utf-8-sig')
