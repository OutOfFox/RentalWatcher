import datetime, hashlib, json, logging, os, requests, subprocess
from bs4 import BeautifulSoup
from pushbullet import Pushbullet
from listingstorage import ListingStorage

CONFIG_FILE = 'config.json'
# config.json requires 3 keys
# {"Pushbullet Key": "",
#  "Kijiji URL":     "https://www.kijiji.ca/<your local listing>",
#  "Castanet URL":   ""
#  "Max Price": 0 (optional)
# }
SEEN_LISTING_FILE = 'seen.json'
CONFIG_PB_KEY = 'Pushbullet Key'
CONFIG_KIJ_KEY = 'Kijiji URL'
CONFIG_CAS_KEY = 'Castanet URL'
CONFIG_MAXP_KEY = 'Max Price'

def in_script_dir(file):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), file)

def scrape_kijiji_rentals(base_url, num_pages):
    all_listings_info = []
    for page_num in range(1, num_pages + 1):
        url = f"{base_url}?page={page_num}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        listings = soup.find_all("div", {"class": "search-item"})

        for listing in listings:
            title = listing.find("a", {"class": "title"}).text.strip()
            price = listing.find("div", {"class": "price"}).text.strip()
            price = float(price.replace("$", "").replace(",", "").replace('Please Contact', '0'))
            location_div = listing.find("div", {"class": "location"})
            city = location_div.find("span").text.strip()
            date_posted = location_div.find("span", {"class": "date-posted"}).text.strip()
            if date_posted == "Yesterday":
                date_posted = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            elif date_posted.startswith("<"):
                date_posted = datetime.datetime.now().strftime("%Y-%m-%d")
            else:
                date_posted = datetime.datetime.strptime(date_posted, "%d/%m/%Y").strftime("%Y-%m-%d")
            description = listing.find("div", {"class": "description"}).text.strip()
            url = "https://www.kijiji.ca" + listing.find("a", {"class": "title"})["href"]

            listing_dict = {
                "title": title,
                "price": price,
                "city": city,
                "date_posted": date_posted,
                "description": description,
                "url": url
            }

            all_listings_info.append(listing_dict)

    return all_listings_info

def scrape_castanet_rentals(base_url, num_pages):
    all_listings_info = []
    for page_num in range(1, num_pages + 1):
        url = f"{base_url}?perpage=50&p={page_num}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        listings = soup.find_all("div", {"class": "classified"})

        for listing in listings:
            title = listing.find("a", {"class": "title"}).text.strip()
            price = listing.find("div", {"class": "price"}).text.strip()
            price = float(price.replace("$", "").replace(",", ""))
            city = listing.find("div", {"class": "city"}).text.strip()
            date_posted = listing.find("div", {"class": "date"}).text.strip()
            if date_posted == "Yesterday":
                date_posted = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            elif date_posted.startswith("<"):
                date_posted = datetime.datetime.now().strftime("%Y-%m-%d")
            else:
                date_posted = datetime.datetime.strptime(date_posted, "%d/%m/%Y").strftime("%Y-%m-%d")
            description = listing.find("div", {"class": "description"}).text.strip()
            url = "https://classifieds.castanet.net" + listing.find("a", {"class": "title"})["href"]

            listing_dict = {
                "title": title,
                "price": price,
                "city": city,
                "date_posted": date_posted,
                "description": description,
                "url": url
            }

            all_listings_info.append(listing_dict)

    return all_listings_info

if __name__ == '__main__':
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f'Starting run at {current_time}.')

    # Config setup - will check current working directory, then script directory.
    cwd = os.path.join(os.getcwd(), CONFIG_FILE)
    scr = in_script_dir(CONFIG_FILE)

    if os.path.isfile(cwd):
        logging.info("Using current directory's config file.")
        config_actual_path = cwd
    elif os.path.isfile(scr):
        logging.info("Using script directory's config file.")
        config_actual_path = scr
    else:
        logging.error(f'Config file "{CONFIG_FILE}" not found.')
        exit()

    with open(config_actual_path, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    # Error checking...
    if CONFIG_PB_KEY not in config or config[CONFIG_PB_KEY] == '':
        logging.error('No Pushbullet key found in config.')
        exit()

    if CONFIG_KIJ_KEY not in config or config[CONFIG_KIJ_KEY] == '':
        logging.error('No Kijiji URL found in config.')
        exit()

    if CONFIG_CAS_KEY not in config or config[CONFIG_CAS_KEY] == '':
        logging.error('No Castanet URL found in config.')
        exit()

    pb = Pushbullet(config[CONFIG_PB_KEY])
    seen_storage = ListingStorage(in_script_dir(SEEN_LISTING_FILE))

    all_listings = scrape_castanet_rentals(config[CONFIG_CAS_KEY], 5) + scrape_kijiji_rentals(config[CONFIG_KIJ_KEY], 2)
    filtered_listings = [listing_dict for listing_dict in all_listings if (int(listing_dict['price']) < 2000) and (not seen_storage.check(listing_dict['url']))]

    # Stop the spam when running for the first time.
    first_run = len(seen_storage.hashed_strings) == 0
    allow_listings_first_run = 3
    frcntr = 0
    for item in filtered_listings:
        message = f"{item['title']} ({item['price']}, {item['city']}, {item['date_posted']})"
        seen_storage.add(item['url'])
        if first_run and frcntr >= allow_listings_first_run:
            continue
        frcntr += 1
        pb.send_message(message, item['url'], item["description"])

    seen_storage.save()
