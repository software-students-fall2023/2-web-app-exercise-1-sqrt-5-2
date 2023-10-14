import json
import os
from db import insert_all

with open(os.path.join('dummy_data', 'food.json'), 'r') as file:
    data = json.load(file)

insert_all('listings', data)