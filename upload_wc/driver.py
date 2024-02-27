from woocommerce import API
import json
import logging
from tqdm import tqdm

from config import WoocommerceConfig
from config import PRICE_INCREASE

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


class WooCommerceDriver:

    def __init__(self, config: WoocommerceConfig) -> None:
        self.api = API(
            url=config.wc_site,
            consumer_key=config.wc_key,
            consumer_secret=config.wc_secret,
            timeout=120
        )
        if self.api.get('products/categories').status_code == 200:
            logging.info('authorization successfully')
        else:
            logging.error('authorization error')

        self.categories = self.get_all_categories()

        self.product_data = []

    def get_all_categories(self) -> dict:
        response = json.loads(self.api.get('products/categories').text)
        
        return {category['id']: category['name'] for category in response}

    def get_all_skus(self) -> dict:
        response = json.loads(self.api.get('products').text)

        return {product['id']: product['sku'] for product in response}

    def get_category(self, name_category: str) -> int:
        for category in self.categories:
            if name_category == category['name']:
                return category['id']

    def delete_all_products(self):
        product_data = json.loads(self.api.get('products').text)

        logging.info('delete all products')
        for product in tqdm(product_data):
            self.api.delete(f'products/{product["id"]}')

    def create_category(self, categories_list: list) -> None:
        self.get_all_categories()

        logging.info('deleted unnecessary categories')
        for category in tqdm(self.categories):
            if category['name'] in categories_list:
                categories_list.remove(category['name'])
            else:
                self.api.delete(f'products/categories/{category["id"]}')

        logging.info('create categories')
        for category in tqdm(categories_list):
            category_data = {
                "name": category,
                "description": "category description"
            }
            self.api.post('products/categories', category_data, params={'force': True})

        self.get_all_categories()

    def add_category(self, categories_list: list) -> int:
        last_id = 0
        for category in categories_list:
            if category in self.categories.values():
                last_id = list(self.categories.keys())[list(self.categories.values()).index(category)]
                # categories_list.remove(category['name'])
            else:
                category_data = {
                    "name": category,
                    "description": "category description",
                    "parent": last_id
                }
                result = json.loads(self.api.post('products/categories', category_data, params={'force': True}).text)
                # print(categories_list)
                # print(self.categories)
                # print(type(last_id))
                # print(last_id)
                # print(result)
                last_id = result['id'] if 'id' in result else result['data']['resource_id']
                self.categories[last_id] = category

        return last_id

    def get_clear_data(self) -> dict:
        return {
            'create': [],
            'update': [],
        }

    def add_products(self, products_list: list) -> None:
        # self.delete_all_products()

        skus = self.get_all_skus()
        counter = 0
        c_hundred = 0
        data = self.get_clear_data()

        logging.info('create new products')
        for product in tqdm(products_list):
            category = self.add_category(product['breadcrumbs'])
            if 'Dimensions' in product['features']:
                dimension = product['features']['Dimensions'].split()
                if len(dimension) > 1:
                    dimension = [dimension[0], dimension[2], dimension[4]]
                else:
                    dimension = [dimension[0], dimension[0], dimension[0]]
            else:
                dimension = ['N/A', 'N/A', 'N/A']

            if product['article'] in skus.values():
                data['update'].append(
                    {
                        'id': list(skus.keys())[list(skus.values()).index(product['article'])],
                        'regular_price': str(product['price'] + product['price'] * PRICE_INCREASE),
                        'stock_quantity': product['in_stock'],
                    }
                )
            else:
                data['create'].append({
                    'name': product['name'],
                    'sku': product['article'],
                    'description': product['description'],
                    'regular_price': str(product['price']+product['price']*PRICE_INCREASE),
                    'on_sale': product['is_available'],
                    'stock_quantity': product['in_stock'],
                    'dimensions': {
                        'length': dimension[0],
                        'width': dimension[1],
                        'height': dimension[2]
                    },
                    'weight': product['features']['Weight'],
                    'meta_data': [{
                        'key': 'maximum_allowed_quantity',
                        'value': str(product['in_stock'])
                    }],
                    'categories': [
                        {
                            # 'id': self.get_category(product['category'])
                            'id': category
                        }
                    ],
                    'images': [
                        {
                            'src': product['image']
                        }
                    ],
                    # 'attributes': [
                    #     {
                    #         'name': list(attribute.keys())[0],
                    #         'visible': True,
                    #         'variation': True,
                    #         'options': [
                    #             attribute[list(attribute.keys())[0]]
                    #         ]
                    #     }
                    #     for attribute in product['features']
                    # ]
                })

            # self.api.post('products', product_data)
            if counter == 99:
                logging.info("Uploading products")

                self.api.post('products/batch', data)
                c_hundred += 1
                counter = 0
                data = self.get_clear_data()

            counter += 1
