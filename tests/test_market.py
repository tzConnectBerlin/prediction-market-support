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

config = Config(config_file="tests/oracle.ini")

def new_market():
    test_accounts = Accounts(folder="tests/users", endpoint="http://localhost:20000")
    new_market = Market(test_accounts, config)
    print(new_market.pm_contracts)
    return new_market

accounts = [
        {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"}
]

questions = [
        ["who", "why", "donald", 1000, 10, 3, 4]
]

expected = [
        []
]

test_data = [
    (accounts[0], new_market(), questions[0], expected[0])
]

client = config["admin_account"]
contract = client.contract(config["contract"])
stablecoins = client.contract(contract.storage["stablecoin"]())

def rand(mul=100):
    return random.randint(1,99) * mul

def finance_account(key: str):
    client = pytezos.using(
            shell="http://localhost:20000",
            key="edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq"
    )
    res = client.transaction(key, amount=Decimal(500)) \
            .autofill().sign().inject()
    print(res)
    sleep(3)

@pytest.mark.parametrize("account,market,data,expected", test_data)
def test_transfer_stablecoin_to_user(account, market, data, expected):
    finance_account(account["key"])
    market.transfer_stablecoin_to_user(account["name"], rand())
    sleep(3)
    balance = stablecoins.storage["ledger"][account["key"]]()
    amount = rand(3000)
    market.transfer_stablecoin_to_user(account["name"], amount)
    sleep(3)
    new_balance = stablecoins.storage["ledger"][account["key"]]()
    assert stablecoins.storage["ledger"][account["key"]]()
    assert balance["balance"] + amount == new_balance["balance"]

@pytest.mark.parametrize("account,market,data,expected", test_data)
def test_ask_question(account, market, data, expected):
    finance_account(account["key"])
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    assert question['total_auction_quantity'] == data[3]
    assert question['state'] == "questionAuctionOpen"
    assert question['owner'] == account["key"]

@pytest.mark.parametrize("account,market,data,expected", test_data)
def test_bid_auction(account, market, data, expected):
    finance_account(account["key"])
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    market.bid_auction(ipfs_hash, account["name"], 100, 10)
    sleep(3)
    bids = question["auction_bids"]
    assert account["key"] in bids

@pytest.mark.parametrize("account,market,data,expected", test_data)
def test_close_auction(account, market, data, expected):
    finance_account(account["key"])
    sleep(3)
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(80)
    market.close_auction(ipfs_hash, account["name"])
    sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionAuctionWithdrawOpen"

@pytest.mark.parametrize("account,market,data,expected", test_data)
def test_close_market(account, market, data, expected):
    finance_account(account["key"])
    sleep(3)
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(130)
    market.close_market(ipfs_hash, True, account["name"])
    sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionMarketClosed"
"""
@pytest.mark.parametrize("account,market,data,expected", test_data)
def test_buy_token(account, market, data, expected):
    finance_account(account["key"])
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(2)
    balance = stablecoins.storage["ledger"][account["key"]]()
    amount = rand(5)
    market.buy_token(ipfs_hash, True, amount, account["name"])
    sleep(2)
    new_balance = stablecoins.storage["ledger"][account["key"]]()
    assert stablecoins.storage["ledger"][account["key"]]()
    assert balance["balance"] - amount == new_balance["balance"]

@pytest.mark.parametrize("account,market,data,expected", test_data)
def test_burn_token(account, market, data, expected):
    finance_account(account["key"])
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(2)
    market.bid_auction(ipfs_hash, account["name"], 100, 10)
    #market.bid_auction(ipfs_hash, account["name"], 100, 10)
    sleep(1)
    amount = 1000
    balance = stablecoins.storage["ledger"][account["key"]]()
    market.burn(ipfs_hash, amount, account["name"])
    sleep(2)
    new_balance = stablecoins.storage["ledger"][account["key"]]()
    print(new_balance)
    assert stablecoins.storage["ledger"][account["key"]]()
    assert balance["balance"] == new_balance["balance"] + amount
"""
