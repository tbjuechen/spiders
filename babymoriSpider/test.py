import requests
from lxml import etree

response = requests.get('https://babymori.com/sitemap_products_1.xml?from=438883007&to=7330521186390')
xml = etree.fromstring(response.content)

items = []
for child in xml:
    for _ in child:
        if _.tag.endswith('loc'):
            items.append(_.text + 'js')

print(items)
