from db import db
from bson.json_util import loads
from defaults import DATA_DIR
from .delete import delete


def add_dummy_data(collection, filename):
    with open(DATA_DIR / filename, 'r', encoding='utf-8') as f:
        db[collection].insert_many(loads(f.read()))


def fill():
    delete()
    for file in DATA_DIR.glob('*.json'):
        print('Filling collection with data from:', file.name)
        add_dummy_data(file.stem, file.name)


if __name__ == '__main__':
    fill()
