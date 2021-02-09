import json
import random

def get_country_and_capital():
    """ Return random country and capital combo"""
    with open('country-by-capital-city.json', 'r') as f:
        data = json.load(f)
        count = len(data)
        #print(data[random.randint(0,count)])
        return data[random.randint(0,count)]

get_country_and_capital()
