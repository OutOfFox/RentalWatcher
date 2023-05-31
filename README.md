# RentalWatcher
 Watches Castanet.net/Kijiji rental listings, notifies user via Pushbullet

# Requirements

Requires bs4 (BeautifulSoup) and requests.

# Config

config.json requires 3 keys, and includes an optional price limit.
```
{
  "Pushbullet Key": "",
  "Kijiji URL":     "https://www.kijiji.ca/b-apartments-condos/<your local listing>",
  "Castanet URL":   "https://classifieds.castanet.net/cat/rentals/"

  "Max Price": 0 (optional, default 1,000,000)
}
```

# File locations

Can be modified by the constants at the top of rental_watcher.py

Config will check current working directory, then script directory for the file.
