from woocommerce import API
from pymongo import MongoClient
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
        self.run()


        self.wcapi = API(
            url="https://alopl.nazwa.pl/wordpress/wpn_nowypress",
            consumer_key="ck_4314dd53858243c893d4268ccbbd47f33a79b311",
            consumer_secret="cs_033f1c30bc58846be334ebfeae444c302a8dd660",
            wp_api=True,
            version="wc/v3"
        )

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
            response = self.create_main_product_woo()
            woo_id = self.get_woo_id()
            self.add_main_woocommerce_id_to_database(woo_id, db_id)

    def add_main_woocommerce_id_to_database(self, woo_id, db_id):
        pass

    def create_main_product_woo(self, name, regular_price, description):
        type = 'simple'
        data = {}
        data['name'] = name
        data['type'] = 'simple'
        data['regular_price'] = regular_price
        data['description'] = description
        # data['categories'] = categories
        # data['images'] = images

        return self.wcapi.post("products", data).json()

    def add_woo_id_to_db(self, woo_prod_id):
        pass

a= SyncDbWoocommerce()