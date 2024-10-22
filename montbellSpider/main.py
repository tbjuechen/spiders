import requests
from lxml import etree
from pandas import DataFrame
from tqdm import tqdm

url:str = 'https://webshop.montbell.jp/goods/list_fo.php?category=789001'

response:requests.Response = requests.get(url)
html = etree.HTML(response.text)

max_page = html.xpath('//span[@class="maxNumber"]/text()')[0]
item_list = []

for i in range(1, int(max_page)+1):
    url = f'https://webshop.montbell.jp/goods/list_fo.php?category=789001&page={i}'
    response:requests.Response = requests.get(url)
    sub_item_list = etree.HTML(response.text).xpath('//div[@class="unit"]')
    item_list.extend(sub_item_list)

print(len(item_list))
item_info_list = []

for item in tqdm(item_list):
    title = item.xpath('div/h3[@class="ttlType03"]/a/@title')[0]
    price = item.xpath('div//p[@class="outlet"]/text()')[0][1:-4].replace(',','')
    number = item.xpath('div/div[@class="specCont"]/div[@class="description"]/p[2]/text()')[0]
    source = item.xpath('div/div[@class="specCont"]/div[@class="description"]/p[3]/text()')[0]
    # weight = item.xpath('div/div[@class="specCont"]/div[@class="description"]/p[4]/text()')[0][6:]
    # describe = item.xpath('div/div[@class="specCont"]/div[@class="description"]/p[5]/text()')[0]
    size = item.xpath('div/div[@class="specCont"]/div[@class="spec"]/div[@class="size"]/p[2]/text()')[0]
    color = item.xpath('div/div[@class="specCont"]/div[@class="spec"]/div[@class="color"]/div[@class="inner"]/p/a/img/@title')
    color = ' | '.join(color)
    item_info_list.append({
        'title': title,
        'price': price,
        'number': number,
        'source': source,
        # 'weight': weight,
        # 'describe': describe,
        'size': size,
        'color': color
    })

data = DataFrame(item_info_list)
data.to_csv('montbell.csv', encoding='utf-8-sig')