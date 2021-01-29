#!/usr/bin/env python3

from collections import ChainMap
import configparser
from datetime import datetime
import jq
import json
import urllib.request

config = configparser.ConfigParser()
config.read('oracle.ini')

BCD_URL = "https://api.better-call.dev/v1/"
NETWORK = "delphinet"

CONTRACT_ID = config['Tezos']['pm_contract']

def load_json(url):
    """ Load JSON from given URL and return as Python object"""
    with urllib.request.urlopen(url) as u:
        data = json.loads(u.read().decode())
        return data

def get_question_data(data):
    """ If this object has a value, return it. If it has children,
    recurse into them. Flatten all the values into one dict."""
    def get_value(js):
        if js.get('value') is not None:
            return js['value']
        if js.get('children') is not None:
            return get_question_data(js['children'])
    ls = list(map(lambda x: {
        x['name'] : get_value(x),
        }, data))
    return dict(ChainMap(*ls))

def get_questions(id):
    """ Load and parse the questions bigmap"""
    url = f"{BCD_URL}bigmap/{NETWORK}/{id}/keys?size=10000"
    js = load_json(url)
    ls = list(map(lambda x : {
        x['data']['key']['value'] : get_question_data(x['data']['value']['children'])
    }, js))
    return jq.first('add', ls)

def get_storage_internal(js):
    """ Internal method which gets the value of a JSON object, or
    those of its children"""
    def get_value(js):
        if js.get('value') is not None:
            return js['value']
        if js.get('children') is not None:
            return get_storage_internal(js['children'])
    return dict(list(map(lambda x :( x['name'], get_value(x) ), js)))

def get_storage(id):
    """ Get all the storage for a contract and pass its children
    to @get_storage_internal """
    url = f"{BCD_URL}/contract/{NETWORK}/{id}/storage?size=10000"
    js = load_json(url)
    storage = get_storage_internal(js['children'])
    return storage

def get_ledger(id):
    """ Get the ledger and pass it to jq to make the keys friendlier"""
    url = f"{BCD_URL}bigmap/{NETWORK}/{id}/keys?size=10000"
    js = load_json(url)
    return jq.first(r'map({ "\(.data.key.children[0].value).\(.data.key.children[1].value)": .data.value.children[0].value }) | add', js)

def get_total_supply(id):
    """ Get the total supply bigmap and flatten it"""
    url = f"{BCD_URL}bigmap/{NETWORK}/{id}/keys?size=10000"
    js = load_json(url)
    return jq.all('map({ (.data.key.value): (.data.value.value) }) | add', js)