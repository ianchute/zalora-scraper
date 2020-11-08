import datetime
import json
import re
import time

import requests


class ZaloraScraper():
    def __init__(
        self,
        user_agent=None,
        root_url=None,
        api_url=None,
    ):
        self.user_agent = \
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36' if user_agent is None \
            else user_agent

        self.root_url = 'https://www.zalora.com.my' if root_url is None else root_url
        self.root_url = self.root_url.strip("/")

        self.api_url = 'https://www.zalora.com.my/_c/v1/desktop/list_catalog_full' if api_url is None else api_url
        self.api_url = self.api_url.strip("/")

        self.headers = {
            'User-Agent': self.user_agent
        }

    def _extract_metadata(self, gender, product, brand, occassion):
        url = f"{self.root_url}/{gender}/{product}/{brand}/?occasion={occassion}"
        text = requests.get(url, headers=self.headers).text

        brand_idx = text.index("brandIds[]")
        brand_code = int(
            re.match("^([0-9]+)", text[brand_idx+11:]).groups()[0])

        category_idx = text.index("categoryId=")
        category_code = int(
            re.match("^([0-9]+)", text[category_idx+11:]).groups()[0])

        return brand_code, category_code

    def _extract_from_api(self, gender, brand_code, category_code, occassion, start, end):
        parameters = [
            f"gender={gender}",
            f"segment={gender}",
            f"category_id={category_code}",
            "sort=popularity",
            "dir=desc",
            f"offset={start}",
            f"limit={end}",
            f"occasion={occassion}",
            f"brand={brand_code}",
            "special_price=false",
            "all_products=false",
            "new_products=false",
            "top_sellers=false",
            "catalogtype=Main",
            "lang=en",
            "is_brunei=false",
            "sort_formula=sum(product(0.01%2Cscore_simple_availability)%2Cproduct(0.0%2Cscore_novelty)%2Cproduct(0.99%2Cscore_product_boost)%2Cproduct(0.0%2Cscore_random)%2Cproduct(1.0%2Cscore_personalization))",
            "search_suggest=false",
            "enable_visual_sort=true",
            "enable_filter_ads=true",
            "compact_catalog_desktop=false",
            "name_search=false",
            "solr7_support=true",
            "pick_for_you=false",
            "learn_to_sort_catalog=false",
            "is_multiple_source=true",
        ]

        try:
            parameters_joined = "&".join(parameters)
            response = requests.get(
                self.api_url + "?" + parameters_joined, headers=self.headers)
            results = json.loads(response.text)["response"]["docs"]
            results = [{
                "brand": x["meta"]["brand"],
                "sku": x["meta"]["sku"],
                "name": x["meta"]["name"],
                "actual_price": x["meta"]["price"],
                "discounted_price": x["meta"]["special_price"],
                "image": x["image"],
            } for x in results]
            return results
        except Exception as e:
            print(e)
            return []

    def scrape(self, gender, product, brand, occassion, batch_size=100, identifier="sku"):
        print("\n\t[ZALORA SCRAPER TOOL]\n")
        ts_start = time.time()
        now = str(datetime.datetime.now()).split(".")[
            0].replace(" ", "-").replace(":", "")
        print(f"\tScraping started at: {now}\n")

        print("\tScraping parameters:")
        print(f"\t\tGender: {gender}")
        print(f"\t\tProduct: {product}")
        print(f"\t\tBrand: {brand}")
        print(f"\t\tOccassion: {occassion}\n")

        brand_code, category_code = self._extract_metadata(
            gender, product, brand, occassion)
        results = []
        batch_num = 0
        skus = set()
        while True:
            start = batch_num * batch_size
            end = (batch_num + 1) * batch_size
            batch = self._extract_from_api(
                gender, brand_code, category_code, occassion, start, end)
            batch = [x for x in batch if x[identifier] not in skus]
            results += batch
            skus |= {x[identifier] for x in batch}
            batch_num += 1
            if len(batch) == 0:
                break
        print("\tFound", len(results), "products!\n")
        filename = f"zalora-{gender}-{product}-{brand}-{occassion}-{now}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=4)
        print(f"\tSaved to file: {filename}\n")
        print(f"\tTook {round(time.time() - ts_start, 2)} seconds\n")
