#!/usr/bin/env python3

"""
    Tooling for prediction markets support
"""

import json
import os
import random
import subprocess
import time
from datetime import datetime, timedelta

import configparser
import ipfshttpclient
import pytz
import typer
from pytezos import pytezos

##### Local Script
import summary

AUCTION_END_DATE=30
MARKET_END_DATE=50

##################
# Setup
##################
app = typer.Typer()
config = configparser.ConfigParser()
config.read('oracle.ini')
pm_contract = pytezos.contract(config['Tezos']['pm_contract'])

users = [
    'alice',
    'ava',
    'pascal'
]

PERCENT = 10000000000000000

accounts = {}
pm_contracts = {}

def instantiate_users(): 
    """
    Get all the user data from the user folder user
    """
    for user in users:
        accounts[user] = pytezos.using(
            key = f"users/{user}.json",
            shell = "http://tezos.newby.org:8732",
        )
        pm_contracts[user] = accounts[user].contract(config['Tezos']['pm_contract'])

##################
# methods
##################

def get_stablecoin(account):
    """
    Return an reference to the stablecoin storage  for account
    """
    stablecoin = account.contract(
        summary.get_storage(config['Tezos']['pm_contract'])['stablecoin']
    )
    return stablecoin

def get_public_key(account):
    """
    Get public key hash from account
    """
    return account.key.public_key_hash()

def activate_user(user: str):
    """
    Activate user
    """
    print(f"Trying to activate account of user {user}: ", end='')
    try:
        accounts[user].activate_account().autofill().sign().inject()
        print(f"account of {user} was activated")
    except Exception:
        print(f"account of user {user} was not activated")

def import_user(user: str):
    """
    Import_user
    """
    print(f"Trying to import account of user {user}: ", end='')
    env = dict(os.environ)
    host = config['Tezos']['endpoint']
    subprocess.run(
        [
            'tezos-client',
            '-E',
            host,
            'import',
            'secret',
            'key',
            user,
            f"unencrypted:{accounts[user].key.secret_key()}",
            '--force'
        ],
        env=env,
        check=False,
    )
    print(f"account of {user} was imported")

def reveal_user(user: str):
    """
    Reveal user
    """
    print(f"Trying to reveal account of user {user}: ", end='')
    try:
        accounts[user].reveal().autofill().sign().inject()
        print(f" account of user {user} was revealed")
    except Exception:
        print(f"account of user {user} was not revealed")

@app.command()
def manage_accounts(
        activate: bool = typer.Option(False, "--activate", "-a"),
        reveal: bool = typer.Option(False, "--reveal", "-r"),
        import_accounts: bool = typer.Option(False, "--import", "-i")
    ):
    "Management of accounts in the user folder"
    instantiate_users()
    with typer.progressbar(users) as progress:
        for user in progress:
            if activate:
                activate_user(user)
            if import_accounts:
                import_user(user)
            if reveal:
                reveal_user(user)

@app.command()
def ask_question(
        question: str,
        answer: str,
        user: str,
        quantity: int = typer.Option(100),
        rate: int = typer.Option(random.randint(1,99) * PERCENT)
    ):
    """
    Create a question in IPFS

    question: string representing the answer asked
    answer: string representing the possible answer
    user: string representing the questions owner
    quantity: integer representing the quantity of stable coin generated
    rate: rate
    """
    instantiate_users()
    if user not in users:
        raise Exception("Missing User")
    timenow = datetime.now().astimezone(pytz.utc)
    auction_end_date = timenow + timedelta(minutes=AUCTION_END_DATE)
    market_close_date = timenow + timedelta(minutes=MARKET_END_DATE)
    param = {
            'auctionEndDate': auction_end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            'iconURL': 'https://images-na.ssl-images-amazon.com/images/I/41GqyirrgbL._AC_SX425_.jpg',
            'marketCloseDate': market_close_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            'question': question,
            'yesAnswer': answer,
    }
    ipfs = ipfshttpclient.connect(config['IPFS']['server'])
    ipfs_hash = ipfs.add_str(json.dumps(param))
    print(f"Created hash {ipfs_hash}")
    print(ipfs.get_json(ipfs_hash))
    pm_contracts[user].createQuestion({
        'auction_end': int(auction_end_date.timestamp()),
        'market_close': int(market_close_date.timestamp()),
        'quantity': quantity,
        'question': ipfs_hash,
        'rate': rate
    }).operation_group.autofill().sign().inject()
    print(f"Created market {ipfs_hash} in PM contract")
    return ipfs_hash

@app.command()
def fund_stablecoin(
        value: int = typer.Option(10000000000000000000)
    ):
    """
    Fund all accounts with a random quantity of tezos

    value: the amont of tezos funded
    """
    instantiate_users()
    for user in users:
        print(f"Transferring to {user}")
        transfer_stablecoin(
            accounts[user].key.public_key_hash(),
            value,
        )
        time.sleep(60)

@app.command()
def transfer_stablecoin(
        dest: str,
        value: int = typer.Option(100000000000000000)
    ):
    """
    Transfer a certain amount of coins toward an user address

    dest: user address that will receive the funds
    """
    admin_account = summary.admin_account()
    stablecoin = get_stablecoin(admin_account)
    stablecoin.transfer({
        'from': get_public_key(admin_account),
        'to': dest,
        'value': value
    }).operation_group.autofill().sign().inject()

@app.command()
def bid_auction(
        ipfs_hash: str,
        user: str,
        quantity: int = typer.Option(50000),
        rate: int = typer.Option(random.randint(1,99) * PERCENT)
    ):
    """
    Launch a bid on an auction

    ipfs_hash: the contract concerned by the bid
    user: string representing the user which is bidding during the auction
    quantity: Integer representing quantity of stable coins bid during the auction
    rate: What is rate?
    """
    print(f"User {user} bidding {rate} on {ipfs_hash}")
    env = dict(os.environ)
    print(user)
    env['ACCOUNT'] =  user
    env['AUCTION'] = ipfs_hash
    env['CONTRACT'] = config['Tezos']['pm_contract']
    env['ENDPOINT'] = config['Tezos']['endpoint']
    env['HOST'] = config['Tezos']['node']
    env['PORT'] = config['Tezos']['port']
    env['QUANTITY'] = str(quantity)
    env['RATE'] = str(rate)
    sub = subprocess.run(["./bid.sh"], env=env, capture_output=True, check=False)
    print(f"{sub.stderr}\n{sub.stdout}")
    _data = {
            'quantity': quantity,
            'question': ipfs_hash,
            'rate': rate
    }
    ## Not working
    ## print(data)
    ##pm_contracts[user].bid(_data).operation_group.autofill(gas_reserve=200000).sign().inject()

@app.command()
def random_bids(
        ipfs_hash: str,
        quantity: int = typer.Option(50000),
        rate: int = typer.Option(random.randint(1,99) * PERCENT)
    ):
    """
    Launch random bid on a auction from all of the user contained in the users folder

    ipfs_hash: Contract on which the bid are made
    """
    if len(users) == 0:
        print("Please add some users before using this functionality")
    instantiate_users()
    with typer.progressbar(users) as progress:
        for user in progress:
            bid_auction(
                ipfs_hash,
                user,
                quantity,
                rate
            )


@app.command()
def close_auction(ipfs_hash: str):
    """
    Close the auction

    ipfs_hash: the hash of the concerned contract
    """
    pm_contracts[users[2]].closeAuction(ipfs_hash).operation_group.autofill().sign().inject()

if __name__ == "__main__":
    app()
