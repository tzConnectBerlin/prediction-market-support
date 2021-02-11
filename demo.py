#!/usr/bin/env python3

import argparse
import configparser
import dateparser
from datetime import datetime, timedelta
import ipfshttpclient
import json
import os
from pytezos import pytezos
import pytz
import random
import subprocess
import summary
import time

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
parser.add_argument('--import-accounts', type=bool, help='Import accounts')
parser.add_argument('--fund-stablecoin', type=bool, help='Fund stablecoin accounts')
parser.add_argument('--transfer-stablecoin', type=ascii, help='Fund stablecoin accounts')
parser.add_argument('--bid-auction', type=ascii, help='Bid on an auction')
parser.add_argument('--close-auction', type=ascii, help='Fund stablecoin accounts')
parser.add_argument('--buy-tokens', type=ascii, help='Buy tokens')
parser.add_argument('--list-auctions', type=ascii, help='List auctions')
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
    'ava',
    'brian',
    'caleb',
    'donald']

PERCENT = 10000000000000000

accounts = {}
pm_contracts = {}

for user in users:
    accounts[user] = pytezos.using(
        key = f"{user}.json",
        shell = "http://tezos.newby.org:8732",
        )

    if args.activate_accounts:
        accounts[user].activate_account().autofill().sign().inject()
    if args.reveal_accounts:
        try:
            accounts[user].reveal().autofill().sign().inject()
        except(Exception):
            pass
    if args.import_accounts:
        subprocess.run(['tezos-client', '-A', config['Tezos']['node'], 'import', 'secret', 'key', user,
                        f"unencrypted:{accounts[user].key.secret_key()}", '--force'])
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
        'iconURL': 'https://images-na.ssl-images-amazon.com/images/I/41GqyirrgbL._AC_SX425_.jpg',
        }
    ipfs = ipfshttpclient.connect(config['IPFS']['server'])
    ipfs_hash = ipfs.add_str(json.dumps(param))
    print(f"Created hash ${ipfs_hash}")
    print(ipfs.get_json(ipfs_hash))
    pm_contracts[user].createQuestion({
        'question': ipfs_hash,
        'auction_end': int(auction_end_date.timestamp()),
        'market_close': int(market_close_date.timestamp()),
        'rate': random.randint(1,99) * PERCENT,
        'quantity': 100,

    }).operation_group.autofill().sign().inject()
    print(f"Created market {ipfs_hash} in PM contract")
    return ipfs_hash

def fund_stablecoin():
    for user in users:
        print(f"Transferring to {user}")
        admin_account = summary.admin_account()
        stablecoin = admin_account.contract(summary.get_storage(config['Tezos']['pm_contract'])['stablecoin'])
        stablecoin.transfer({
            'from': admin_account.key.public_key_hash(),
            'to': accounts[user].key.public_key_hash(),
            'value': 10000000000000000000
            }).operation_group.autofill().sign().inject()
        time.sleep(60)


def transfer_stablecoin(dest):
    admin_account = summary.admin_account()
    stablecoin = admin_account.contract(summary.get_storage(config['Tezos']['pm_contract'])['stablecoin'])
    stablecoin.transfer({
        'from': admin_account.key.public_key_hash(),
        'to': dest,
        'value': 1000000000000000000000000
    }).operation_group.autofill().sign().inject()

def bid_auction(ipfs_hash):
    for user in users:
        rate = random.randint(1,99) * PERCENT
        print(f"User {user} bidding {rate} on {ipfs_hash}")
        d = dict(os.environ)
        d['AUCTION'] = ipfs_hash
        d['HOST'] = config['Tezos']['node']
        d['PORT'] = config['Tezos']['port']
        d['ACCOUNT'] = user
        d['CONTRACT'] = config['Tezos']['pm_contract']
        d['RATE'] = str(rate)
        d['QUANTITY'] = "50000000000000000000"
        s = subprocess.run(["./bid.sh"], env=d, capture_output=True)
        print(f"{s.stderr}\n{s.stdout}")
        # data = {
        #     'question': ipfs_hash,
        #     'rate': rate,
        #     'quantity': 50000000000000000000,

        #     }
        # print(data)
        # pm_contracts[user].bid(data).operation_group.autofill(gas_reserve=200000).sign().inj

# def buy_tokens(ipfs_hash):
#     for user in users:
#         params = {
#             'question' : ipfs_hash,
#             'coin_quantity': 10,
#             'deadline':

def close_auction(ipfs_hash):
       pm_contracts[users[2]].closeAuction(ipfs_hash).operation_group.autofill().sign().inject()

if args.list_auctions is not None:
    list_auctions()

if args.ask_question is not None:
    create_question(args.ask_question.strip("'"), args.answer.strip("'"), 'caleb')

if args.fund_stablecoin is not None:
    fund_stablecoin()

if args.transfer_stablecoin is not None:
    transfer_stablecoin(args.transfer_stablecoin.strip("'"))

if args.bid_auction is not None:
    bid_auction(args.bid_auction.strip("'"))

if args.close_auction is not None:
    close_auction(args.close_auction.strip("'"))
