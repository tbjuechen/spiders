import requests
from DrissionPage import ChromiumPage
import json
import copy
import pandas
from tqdm import tqdm
import os
import concurrent.futures
from lxml import etree

# broswer = ChromiumPage()
# broswer.get('https://babymori.com/collections/sale')

# items = broswer.eles('.h6')
# items = [item.ele('tag:a').link+'.js' for item in items]
# broswer.quit()

response = requests.get('https://babymori.com/sitemap_products_1.xml?from=438883007&to=7330521186390')
xml = etree.fromstring(response.content)

items = []
for child in xml:
    for _ in child:
        if _.tag.endswith('loc'):
            items.append(_.text + '.js')


datas:list = []

if not os.path.exists('images'):
    os.makedirs('images')

for item in tqdm(items):
    try:
        json_string = requests.get(item).text
        json_data = json.loads(json_string)
        price_parser = lambda x: x[:-2] + '.' + x[-2:]
        original_price = price_parser(str(json_data['compare_at_price']))
        name = json_data['handle']
        id = json_data['id']
        category_ans = {
            'name' : name,
            'id' : id,
            'original_price' : original_price,
        }
        options = json_data['options']
        variants = json_data['variants']

        def download_image(image_url, save_path):
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                with open(save_path, 'wb') as file:
                    file.write(response.content)
                # print(f'Image successfully downloaded and saved to {save_path}')
            except requests.exceptions.RequestException as e:
                print(f'Error downloading the image from {image_url}: {e}')

        def download_images_concurrently(image_urls, save_directory='images'):
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {
                    executor.submit(
                        download_image, 
                        'https:' + image_url, 
                        os.path.join(save_directory, f'[{name}]'+image_url.split('/')[-1].split('?')[0])
                    ): image_url for image_url in image_urls
                }
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f'Error occurred when downloading {url}: {e}')

        # 提取图片 URL 列表
        image_urls = json_data['images']

        # 使用多线程下载图片
        download_images_concurrently(image_urls)

        for _ in variants:
            ans = copy.deepcopy(category_ans)
            ans['current_price'] = price_parser(str(_['price']))
            for option in options:
                ans[option['name']] = _['option'+str(option['position'])]
            ans['sku'] = _['sku']
            ans['title'] = _['title']
            ans['available'] = _['available']
            datas.append(ans)
    except Exception as e:
        continue

df = pandas.DataFrame(datas)
df.to_csv('data.csv', index=False)