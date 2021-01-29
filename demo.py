#!/usr/bin/env python3

import argparse
import configparser
import dateparser
from datetime import datetime, timedelta
import ipfshttpclient
import json
from pytezos import pytezos
import pytz
import random
import wolframalpha

##################
# Arg parsing
##################
parser = argparse.ArgumentParser(
    description = "Demo the Prediction Market.")
parser.add_argument('--question-id', metavar='Q', type=ascii,
                    help='The question id (IPFS hash)')
parser.add_argument('--ask-question', metavar='Z', type=ascii,
                    help='Ask a particular question. If no argument present, one is generated.')
parser.add_argument('--answer', metavar='A', type=ascii,
                    help='The answer')
parser.add_argument('--activate-accounts', type=bool, help='Activate accounts')
parser.add_argument('--reveal-accounts', type=bool, help='Reveal accounts')
args = parser.parse_args()

# if (args.question_id is not None and args.ask_question is not None) or (args.question_id is None and args.ask_question is None):
#     exit("Exactly one of --ask-question and --question-id must be specified")
if (args.ask_question is not None and args.answer is None):
    exit("You must specify an answer if you give a question")

##################
# Setup
##################
config = configparser.ConfigParser()
config.read('oracle.ini')
pm_contract = pytezos.contract(config['Tezos']['pm_contract'])

users = [
    'alice',
    'bob',
    'caleb',
    'donald']

accounts = {}
pm_contracts = {}

for user in users:
    accounts[user] = pytezos.using(
        key = f"{user}.json",
        shell = "delphinet",
        )
    if args.activate_accounts:
        accounts[user].activate_account().fill().sign().inject()
    if args.reveal_accounts:
        accounts[user].reveal().autofill().sign().inject()
    pm_contracts[user] = accounts[user].contract(config['Tezos']['pm_contract'])

##################
# methods
##################
def get_country_and_capital():
    """ Return random country and capital combo"""
    with open('country-by-capital-city.json', 'r') as f:
        data = json.load(f)
        count = len(data)
        return data[random.randint(0,count)]

def create_question(question, answer, user):
    """Create a question in IPFS"""
    timenow = datetime.now().astimezone(pytz.utc)
    auction_end_date = timenow + timedelta(minutes=5)
    market_close_date = timenow + timedelta(minutes=10)
    param = {
        'question': question,
        'yesAnswer': answer,
        'auctionEndDate':  auction_end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        'marketCloseDate': market_close_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        'iconUrl': 'https://images-na.ssl-images-amazon.com/images/I/41GqyirrgbL._AC_SX425_.jpg',
        }
    ipfs = ipfshttpclient.connect(config['IPFS']['server'])
    ipfs_hash = ipfs.add_str(json.dumps(param))
    print(f"Created hash ${ipfs_hash}")
    print(ipfs.get_json(ipfs_hash))
    pm_contracts[user].createQuestion({
        'question': ipfs_hash,
        'auction_end': int(auction_end_date.timestamp()),
        'market_close': int(market_close_date.timestamp()),
    }).inject()
    print("Created market in PM contract")


if args.ask_question is not None:
    create_question(args.ask_question, args.answer, 'alice')
