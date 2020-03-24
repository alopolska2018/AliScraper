from woocommerce import API
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import requests
from requests import Timeout
import time
import datetime

class SyncDbWoocommerce():

    def __init__(self):
        self.client = MongoClient()
        self.client = MongoClient('localhost', 27017)
        db = self.client['ali']
        self.collection = db['ali_tb']
        self.wcapi = API(
            url="http://server764802.nazwa.pl/wordpress",
            consumer_key="ck_28c44a0b2526deeac2791f629e51a394f281b1ad",
            consumer_secret="cs_30e4817bbba122d6cf28c694d14f58f4c061bdbe",
            wp_api=True,
            version="wc/v3",
            timeout = 30
        )
        self.run()

    def run(self):
        self.check_unadded_products_in_woocommerce()

    def get_woo_id(self, response):
        return response['id']

    def check_unadded_products_in_woocommerce(self):
        unadded_products = self.collection.find({"woocommerce_id": 0})
        for product in unadded_products:
            db_id = product['_id']
            name = product['data']['product_name']
            #TODO Figure out what price to put in main product
            regular_price = '15'
            description = product['data']['description']
            #TODO Create mapping between ali_categories and woo
            #categories = product['categories']
            images = product['data']['images']
            # attributes = []
            variants = self.get_all_variants_of_product(db_id)
            attributes_properties = self.get_main_product_attributes(variants)


            response = self.create_main_product_woo(name, regular_price, description, attributes_properties)
            woo_id = self.get_woo_id(response)
            self.add_main_woocommerce_id_to_database(woo_id, db_id)

            self.get_all_variants_attributes(variants)
            self.create_variants_woo(woo_id, db_id, variants)
            print('aa')

    def add_main_woocommerce_id_to_database(self, woo_id, db_id):
        self.collection.find_one_and_update({'_id': ObjectId(db_id)}, {'$set': {'woocommerce_id': woo_id}}, upsert=True)

    def create_main_product_woo(self, name, regular_price, description, attributes_properties):
        data = {}

        data['name'] = name
        data['type'] = 'variable'
        data['regular_price'] = regular_price
        data['description'] = description
        data['attributes'] = attributes_properties
        # data['categories'] = categories
        # data['images'] = images
        response = self.wcapi.post("products", data).json()
        return response

    def test(self):
        variants = self.get_all_variants_of_product('5e70cb5d3364872c3599445a')
        attributes_properties_list = self.get_main_product_attributes(variants)
        self.create_variants_woo('5e70cb5d3364872c3599445a', '231', variants)

    def get_all_variants_of_product(self, db_id):
        item = self.collection.find_one({'_id': ObjectId(db_id)})
        return item['data']['products']

    def get_all_variants_attributes(self, variants):
        available_attributes = {}
        colour_list = []
        size_list = []
        length_list = []
        available_attributes['colour'] = colour_list
        available_attributes['size'] = size_list
        available_attributes['length'] = length_list
        for key, val in variants.items():
            if 'colour' in val:
                colour = val['colour']
                if colour not in colour_list:
                    colour_list.append(colour)

            if 'size' in val:
                size = val['size']
                if size not in size_list:
                    size_list.append(size)

            if 'length' in val:
                length = val['length']
                if length not in length_list:
                    length_list.append(length)

        return available_attributes

    def get_variant_attributes(self, val):
        attributes = []

        if 'colour' in val:
            colour = val['colour']

            attribute = {}
            attribute['id'] = 24
            attribute['option'] = colour
            attributes.append(attribute)

        if 'size' in val:
            size = val['size']

            attribute = {}
            attribute['id'] = 6
            attribute['option'] = size
            attributes.append(attribute)

        if 'length' in val:
            length = val['length']

            attribute = {}
            attribute['id'] = 8
            attribute['option'] = length
            attributes.append(attribute)

        return attributes


    def create_variant_dict(self, sku, variation, attributes):
        data = {}
        image = {}
        image['src'] = variation['img_url']
        #TODO Calculate regular price
        data['regular_price'] = variation['price']
        data['manage_stock'] = True
        data['stock_quantity'] = variation['qty']
        data['sku'] = sku
        data['image'] = image
        data['attributes'] = attributes

        # response = self.wcapi.post("products/{}/variations".format(woo_id), data).json()
        return data

    def add_variant_woocommerce_id_to_database(self, woo_id, db_id, sku):
        self.collection.find_one_and_update({'_id': ObjectId(db_id)}, {'$set': {'data.products.{}.woocommerce_variant_id'.format(sku): woo_id}}, upsert=True)

    def add_variant_to_woo_batch(self, variants, woo_id):
        data = {}
        data['create'] = variants
        try:
            response = self.wcapi.post("products/{}/variations/batch".format(woo_id), data).json()
        except requests.exceptions.Timeout:
            print('Timeout occurred')

        print(response)

    def create_variants_woo(self, woo_id, db_id, variants):
        final_variants_list = []

        for key, value in variants.items():
            attributes = self.get_variant_attributes(value)
            data = self.create_variant_dict(key, value, attributes)
            #TODO ADD CREATED VARIANT ID TO DATABASE
            # self.add_variant_woocommerce_id_to_database(woo_id, db_id, key)
            final_variants_list.append(data)
        print(final_variants_list)
        if len(final_variants_list) > 100:
            raise Exception('Maximum variants for one product is 100')
        else:
            self.add_variant_to_woo_batch(final_variants_list, woo_id)


    def get_main_product_attributes(self, variants):
        attributes_properties_list = []
        attributes =  self.get_all_variants_attributes(variants)
        counter = 0
        #TODO Create a function that will read avaiable attributes from woo and creat not existing
        for key, val in attributes.items():
            if val:
                if key == 'colour':
                    id = 24
                elif key == 'length':
                    id = 8
                elif key == 'size':
                    id = 6
                else:
                    raise Exception('No attributes available for {}'.format(key))

                attributes_properties_dict = {}
                attributes_properties_dict['id'] = id
                # attributes_properties_dict['name'] = name
                attributes_properties_dict['position'] = counter
                attributes_properties_dict['visible'] = True
                attributes_properties_dict['variation'] = True
                attributes_properties_dict['options'] = val
                attributes_properties_list.append(attributes_properties_dict)
                counter += 1

        return attributes_properties_list

a = SyncDbWoocommerce()