from db import drop_collection, db
from bson.json_util import loads
from defaults import DATA_DIR


def fill_collection(collection, filename):
    with open(DATA_DIR / filename, 'r', encoding='utf-8') as f:
        db[collection].insert_many(loads(f.read()))


if __name__ == '__main__':
    for file in DATA_DIR.glob('*.json'):
        drop_collection(file.stem)
        print('Filling collection with data from:', file.name)
        fill_collection(file.stem, file.name)
