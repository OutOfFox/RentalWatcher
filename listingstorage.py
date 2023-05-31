import datetime, hashlib, json, logging, os

class ListingStorage:

    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.hashed_strings = []
        if os.path.isfile(json_file_path):
            self.load()

    def add(self, input_string):
        hash_object = hashlib.md5(input_string.encode())
        hashed_string = hash_object.hexdigest()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.hashed_strings.append({"hashed": hashed_string, "datetime": now})

    def check(self, input_string):
        hash_object = hashlib.md5(input_string.encode())
        hashed_string = hash_object.hexdigest()
        for s in self.hashed_strings:
            if s["hashed"] == hashed_string:
                return True
        return False

    def save(self):
        with open(self.json_file_path, "w", encoding='utf-8') as f:
            json.dump(self.hashed_strings, f)

    def load(self):
        if not os.path.isfile(self.json_file_path):
            msg = f"File {self.json_file_path} does not exist. Cannot be loaded."
            logging.error(msg)
            raise FileNotFoundError(msg)
        with open(self.json_file_path, "r", encoding='utf-8') as f:
            self.hashed_strings = json.load(f)
            # Remove any listings added more than 60 days ago
            now = datetime.datetime.now()
            self.hashed_strings = [s for s in self.hashed_strings if (now - datetime.datetime.strptime(s["datetime"], "%Y-%m-%d %H:%M:%S")).days < 60]
