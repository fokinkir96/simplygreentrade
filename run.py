import json

from simply_parser import SimplyGreenTrade
from config import BASE_DIR, load_config
from upload_wc import WooCommerceDriver


def run() -> None:
    config = load_config(BASE_DIR / '.env.dist')

    sgt = SimplyGreenTrade(BASE_DIR, config.simply_config)
    sgt.parse_catalog()
    # with open('result.json', 'w+', encoding='utf-8') as file:
    #     json.dump(sgt.all_products, file, indent=4, ensure_ascii=False)

    # with open('result.json', encoding='utf-8') as f:
    #     all_products = json.loads(f.read())

    # cats = {}
    # for p in all_products:
    #     bread = p['breadcrumbs']
    #     cats[bread[0]] = {}
    #     cats[bread[0]][bread[1]] = {}
    #     cats[bread[0]] = {}
        # this = cats
        # for cat in bread:
        #     this[cat] = {}
        #     this =
    # catalog_url = sgt.catalog_urls
    # print(catalog_url)
    # print(sgt.all_products)
    #
    # catalog = [category.split('/')[-2] for category in catalog_url]
    #
    wc_driver = WooCommerceDriver(config.wc_config)
    # wc_driver.create_category(catalog)
    wc_driver.add_products(sgt.all_products)
    # wc_driver.add_products(all_products)


if __name__ == '__main__':
    run()
