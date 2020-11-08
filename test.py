from zalora_scraper import ZaloraScraper

scraper = ZaloraScraper()
scraper.scrape(
    gender="women",
    product="shoes",
    brand="aldo",
    occassion="Casual"  # note: occassion is case-sensitive
)
