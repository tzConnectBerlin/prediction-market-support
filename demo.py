#!/usr/bin/env python3
import argparse
import configparser
import dateparser
import ipfshttpclient
import json
import os
import pytz
import random
import subprocess
import time
import typer

from pytezos import pytezos
from datetime import datetime, timedelta

##### Local Script 
import summary

##################
# Setup
##################
app = typer.Typer()
config = configparser.ConfigParser()
config.read('oracle.ini')
pm_contract = pytezos.contract(config['Tezos']['pm_contract'])

users = [
        'caleb',
        'donald'
        ]

PERCENT = 10000000000000000

accounts = {}
pm_contracts = {}

for user in users:
    accounts[user] = pytezos.using(
            key = f"users/{user}.json",
            shell = "http://tezos.newby.org:8732",
            )
    #if args.activate_accounts:
    #    accounts[user].activate_account().autofill().sign().inject()
    #if args.reveal_accounts:
    #    try:
    #        accounts[user].reveal().autofill().sign().inject()
    #    except(Exception):
    #        pass
    #if args.import_accounts:
    #    subprocess.run(['tezos-client', 'import', 'secret', 'key', user,
    #                    f"unencrypted:{accounts[user].key.secret_key()}", '--force'])
    pm_contracts[user] = accounts[user].contract(config['Tezos']['pm_contract'])

##################
# methods
##################
@app.command()
def create_question(question: str, answer: str, user: str):
    """Create a question in IPFS"""
    if user not in users:
        raise Exception("Missing User");
    timenow = datetime.now().astimezone(pytz.utc)
    auction_end_date = timenow + timedelta(minutes=5)
    market_close_date = timenow + timedelta(minutes=50)
    param = {
            'question': question,
            'yesAnswer': answer,
            'auctionEndDate':  auction_end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            'marketCloseDate': market_close_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            'iconURL': 'https://images-na.ssl-images-amazon.com/images/I/41GqyirrgbL._AC_SX425_.jpg',
            }
    ipfs = ipfshttpclient.connect(config['IPFS']['server'])
    ipfs_hash = ipfs.add_str(json.dumps(param))
    print(f"Created hash {ipfs_hash}")
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

@app.command()
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


@app.command()
def transfer_stablecoin(dest):
    admin_account = summary.admin_account()
    stablecoin = admin_account.contract(summary.get_storage(config['Tezos']['pm_contract'])['stablecoin'])
    stablecoin.transfer({
        'from': admin_account.key.public_key_hash(),
        'to': dest,
        'value': 1000000000000000000000000
        }).operation_group.autofill().sign().inject()

@app.command()
def bid_auction(ipfs_hash: str, user:str , quantity: int, rate: int):
    rate
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
    data = {
            'question': ipfs_hash,
            'rate': rate,
            'quantity': quantity,
    }
    ## Not working
    ## print(data)
    ## pm_contracts[user].bid(data).operation_group.autofill(gas_reserve=200000).sign().inj

@app.command()
def random_bids(ipfs_hash):
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
        data = {
                'question': ipfs_hash,
                'rate': rate,
                'quantity': 50000000000000000000,
        }
         #Not working
        print(data)
        pm_contracts[user].bid(data).operation_group.autofill(gas_reserve=200000).sign().inj


@app.command()
def close_auction(ipfs_hash: str):
    pm_contracts[users[2]].closeAuction(ipfs_hash).operation_group.autofill().sign().inject()

if __name__ == "__main__":
    app()
