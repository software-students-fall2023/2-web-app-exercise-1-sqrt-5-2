import json
from db import insert_all
from defaults import DATA_DIR

def fill_collection(collection, filename):  
    with open(DATA_DIR / filename, 'r', encoding='utf-8') as f:
        insert_all(collection, json.load(f))

if __name__ == '__main__':
    for file in DATA_DIR.glob('*.json'):
        print('Filling collection', file.stem, 'with data from:', file.name)
        fill_collection(file.stem, file.name)


