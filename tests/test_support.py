import random
import sys
from time import sleep

import configparser
import pytest
from decimal import Decimal
from pytezos import pytezos, Key

from src.accounts import Accounts
from src.config import Config
from src.market import Market
from src.utils import summary


def new_market():
    test_accounts = Accounts(folder="tests/users", endpoint="http://localhost:20000")
    config = Config(config_file="oracle.ini")
    new_market= Market(test_accounts, config)
    return new_market

accounts = [
        {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"}
]

questions = [
        ["who", "why", "donald", 300, 50, 30, 50]
]

test_data = [
    (accounts[0], new_market(), questions[0])
]

def rand(mul):
    return random.randint(1,99) * mul

def finance_account(key: str):
    client = pytezos.using(
            shell="http://localhost:20000",
            key="edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq"
    )
    client.transaction(key, amount=Decimal(1)) \
            .autofill().sign().inject()
    sleep(3)

@pytest.mark.parametrize("account,market,data", test_data)
def test_fund_stablecoin(account, market, data):
    finance_account(account["key"])
    market.transfer_stablecoin_to_user(account, rand() * 100)
    sleep(3)
    balance = stablecoins.storage["ledger"][expected]()
    amount = rand() * 100
    new_market.transfer_stablecoin_to_user(account, amount)
    sleep(3)
    new_balance = stablecoins.storage["ledger"][market]()
    assert stablecoins.storage["ledger"][market]()
    assert balance["balance"] + amount == new_balance["balance"]

@pytest.mark.parametrize("account,market,data", test_data)
def test_ask_question(account, market, data):
    finance_account(account["key"])
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    assert question['total_auction_quantity'] == data[3]
    assert question['state'] == "questionAuctionOpen"
    assert question['owner'] == account.name  #check timestamps

@pytest.mark.parametrize("account,market,data", test_data)
def test_bid_auction(account, market, data):
    finance_account(account["key"])
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    market.bid_auction(ipfs_hash, account.name, 100, 10)
    sleep(3)
    bids = question["auction_bids"]
    assert account.key in bids

@pytest.mark.parametrize("account,market,data", test_data)
def test_close_auction(account, market, data):
    finance_account(account["key"])
    sleep(3)
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(80)
    new_market.close_auction(ipfs_hash, account["name"])
    sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionAuctionWithdrawOpen"

@pytest.mark.parametrize("account,market,data", test_data)
def test_close_market(account,market,data):
    finance_account(account["key"])
    sleep(3)
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(60)
    new_market.close_market(ipfs_hash, True, account["name"])
    sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionMarketClosed"

"""
@pytest.mark.parametrize("account,market,data", test_data)
def test_buy_token():
    finance_account(account["name"])
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(3)
    balance = stablecoins.storage["ledger"][account["key"]]()
    amount = rand(mul)
    new_market.buy_token(ipfs_hash, True, amount, account["name"])
    sleep(3)
    new_balance = stablecoins.storage["ledger"][account["key"]]()
    assert stablecoins.storage["ledger"][account["key"]]()
    assert balance["balance"] - amount == new_balance["balance"]

@pytest.mark.parametrize("account,market,data", test_data)
def test_burn_token():
    finance_account(account["name"])
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(3)
    balance = stablecoins.storage["ledger"][account["key"]]()
    amount = rand()
    new_market.burn(ipfs_hash, amount, account["name"])
    sleep(3)
    new_balance = stablecoins.storage["ledger"][account["key"]]()
    assert stablecoins.storage["ledger"][account["key"]]()
    assert balance["balance"] == new_balance["balance"] + amount
"""
