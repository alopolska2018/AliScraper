import scrapy
import js2xml

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        self.num_of_attr = 0

    def get_category_id(self, data):
        return data['categoryId']
    def get_description_url(self, data):
        return data['descriptionUrl']
    def get_images(self, data):
        return data['imagePathList']
    def get_avail_qty(self, data):
        return data['totalAvailQuantity']

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

            # for sad in zip(item[0], item[1]):
            #     print(sad)
          # for item in item['skuPropertyValues']:
          #     variant = {}
          #     print(item)
        variant = {}
        first_property = {}
        second_property = {}
        # first_property = data[0]
        # variant['32132131'] =
    def get_prices(self, price_array, products):
        price_dict = {}
        # print(price_array)
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

    # def get_shipping(self, products):

    def parse_dict(self, dict):
        # category_id = self.get_category_id(dict['data'])
        # description_url = self.get_description_url(self, dict['descriptionModule'])
        # images = self.get_images(dict['imageModule'])
        # avail_qty = self.get_avail_qty(dict['data']['actionModule'])
        products_array = dict['data']['skuModule']['productSKUPropertyList']
        price_array = dict['data']['skuModule']['skuPriceList']
        products = self.create_products(products_array)
        products = self.get_prices(price_array, products)

    def start_requests(self):
        urls = [
            'https://pl.aliexpress.com/item/32961815719.html'
        ]
        for url in urls:
            # site = pol & c_tp = PLN & x_alimid = 1950647284 & isb = y & ups_u_t = 1614923008279 & region = PL & b_locale = pl_PL & ae_u_p_s = 0
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # selector = scrapy.Selector(text=html, type="html")
        js = response.xpath('/html/body/script[11]/text()').extract_first()
        jstree = js2xml.parse(js)
        dict = js2xml.make_dict(jstree.xpath('//assign[left//identifier[@name="runParams"]]/right/*')[0])
        self.parse_dict(dict)
        print(dict)
