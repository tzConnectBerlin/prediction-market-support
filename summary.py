#!/usr/bin/env python3

from collections import ChainMap
import configparser
from datetime import datetime
import jq
import json
import urllib.request

config = configparser.ConfigParser()
config.read('oracle.ini')

bcd_url = "https://api.better-call.dev/v1/"
network = "delphinet"

contract_id = config['Tezos']['pm_contract']

def load_json(url):
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())
        return data

def get_question_data(data):
    def get_value(js):
        if js.get('value') != None:
            return js['value']
        if js.get('children') != None:
            return get_question_data(js['children'])
    ls = list(map(lambda x: {
        x['name'] : get_value(x),
        }, data))
    return dict(ChainMap(*ls))

def get_questions(id):
    url = f"{bcd_url}bigmap/{network}/{id}/keys?size=10000"
    js = load_json(url)
    ls = list(map(lambda x : {
        x['data']['key']['value'] : get_question_data(x['data']['value']['children'])
    }, js))
    return jq.first('add', ls)

def get_storage_internal(js):
    def get_value(js):
        if js.get('value') != None:
            return js['value']
        if js.get('children') != None:
            return get_storage_internal(js['children'])
    return dict(list(map(lambda x :( x['name'], get_value(x) ), js)))

def get_storage(id):
    url = f"{bcd_url}/contract/{network}/{id}/storage?size=10000"
    js = load_json(url)
    storage = get_storage_internal(js['children'])
    return storage

def get_ledger(id):
    url = f"{bcd_url}bigmap/{network}/{id}/keys?size=10000"
    js = load_json(url)
    return jq.first('map({ "\(.data.key.children[0].value).\(.data.key.children[1].value)": .data.value.children[0].value }) | add', js)

def get_total_supply(id):
    url = f"{bcd_url}bigmap/{network}/{id}/keys?size=10000"
    js = load_json(url)
    return jq.all('map({ (.data.key.value): (.data.value.value) }) | add', js)
