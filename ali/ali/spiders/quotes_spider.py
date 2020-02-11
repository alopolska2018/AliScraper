import scrapy
import js2xml
from ..items import AliItem
from inscriptis import get_text
import requests

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        self.num_of_attr = 0

    def get_category_id(self, data):
        return data['categoryId']
    def get_images(self, data):
        return data['imagePathList']
    def get_shop_info(self, data):
        shop_info = []
        shop_info['shop_url'] = data['storeURL']
        shop_info['shop_location'] = data['detailPageUrl']
        shop_info['shop_followers'] = data['followingNumber']
        shop_info['shop_followers'] = data['followingNumber']
        shop_info['shop_positive_rate'] = data['positiveRate']
        shop_info['storeName'] = data['storeName']
        return shop_info

    def create_products(self, data):
        products = {}
        self.num_of_attr = len(data)

        for item in data[0]['skuPropertyValues']:
            product = {}
            color = item['propertyValueName']
            img_url = item['skuPropertyImagePath']
            attr1_id = data[0]['skuPropertyId']
            attr1_value = item['propertyValueId']
            product['color'] = color
            product['img_url'] = img_url
            product['attr1_id'] = attr1_id
            product['attr1_value'] = attr1_value
            if self.num_of_attr == 1:
                sku = 213124
                products[sku] = product

            try:
                for item in data[1]['skuPropertyValues']:
                    product = {}
                    size = item['propertyValueName']
                    attr2_id = data[1]['skuPropertyId']
                    attr2_value = item['propertyValueId']

                    product['color'] = color
                    product['img_url'] = img_url
                    product['attr1_id'] = attr1_id
                    product['attr1_value'] = attr1_value

                    product['size'] = size
                    product['attr2_id'] = attr2_id
                    product['attr2_value'] = attr2_value
                    sku = '12345' + '-' + product['color'] + '-' + product['size']
                    products[sku] = product
            except IndexError:
                pass
        try:
                for item in data[2]['skuPropertyValues']:
                    if item['skuPropertySendGoodsCountryCode'] == 'CN':
                        attr3_value = item['propertyValueId']
                    else:
                        # TODO EXCPTION, DO NO CREATE PRODUCT WITHOUT SHIPPNG FROM CHINA
                        pass
                    for key, val in products.items():
                        val['attr3_value'] = attr3_value
        except IndexError:
                    pass
        return products

    def get_prices(self, price_array, products):
        price_dict = {}
        for item in price_array:
            sku_attr_id = item['skuPropIds']
            price_dict[sku_attr_id] = item

        for key, value in products.items():
            products_price_dict = {}
            if self.num_of_attr == 1:
                price_dict_key = '{}'.format(value['attr1_value'])
            elif self.num_of_attr == 2:
                price_dict_key = '{},{}'.format(value['attr1_value'], value['attr2_value'])
            elif self.num_of_attr == 3:
                price_dict_key = '{},{},{}'.format(value['attr1_value'], value['attr2_value'], value['attr3_value'])

            price = price_dict[price_dict_key]['skuVal']['actSkuCalPrice']
            qty = price_dict[price_dict_key]['skuVal']['inventory']
            products_price_dict['price'] = price
            products_price_dict['qty'] = qty

            products[key]['price'] = price
            products[key]['qty'] = qty
        return products

    def get_shipping_json(self, product_id):
        shipping_json = requests.get('https://pl.aliexpress.com/aeglodetailweb/api/logistics/freight?productId={}'.format(product_id),
                         headers={'Accept': 'application/json',
                                  'Referer': 'https://pl.aliexpress.com/item/{}.html'.format(product_id)}).json()
        return shipping_json

    def check_free_shipping(self, product_id):
        shipping_json = self.get_shipping_json(product_id)
        shipping_list = shipping_json['body']['freightResult']
        for item in shipping_list:
            price = item['freightAmount']['value']
            if price == 0:
                return True
        return False

    def parse_description(self, response):
        items = AliItem()
        html = response.text
        text = get_text(html)
        items['description'] = text
        return items

    def get_description_url(self, data):
        url = data['descriptionUrl']
        return url

    def parse_dict(self, dict, items):

        products_array = dict['data']['skuModule']['productSKUPropertyList']
        price_array = dict['data']['skuModule']['skuPriceList']
        description_module = dict['data']['descriptionModule']
        shipping_module = dict['data']['shippingModule']
        action_module = dict['data']['actionModule']
        image_module = dict['data']['imageModule']
        store_module = dict['data']['storeModule']

        category_id = self.get_category_id(action_module)
        images = self.get_images(image_module)
        shop_info = self.get_shop_info(store_module)

        url = self.get_description_url(description_module)
        items['desc_url'] = url
        product_id = action_module['productId']
        items['product_id'] = product_id

        products = self.create_products(products_array)
        products = self.get_prices(price_array, products)

        return products

    def start_requests(self):
        urls = [
            'https://pl.aliexpress.com/item/32958589780.html'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        items = AliItem()
        # selector = scrapy.Selector(text=html, type="html")
        js = response.xpath('/html/body/script[11]/text()').extract_first()
        jstree = js2xml.parse(js)
        dict = js2xml.make_dict(jstree.xpath('//assign[left//identifier[@name="runParams"]]/right/*')[0])

        products = self.parse_dict(dict, items)
        items['products'] = products
        url = items['desc_url']
        product_id = items['product_id']
        free_shipping = self.check_free_shipping(product_id)


        yield scrapy.Request(url=url, callback=self.parse_description)


        # yield scrapy.Request(url=url2, callback=self.get_shipping, headers = {'Accept': 'application/json',
        #                           'Referer': 'https://pl.aliexpress.com/item/32969050947.html'} )