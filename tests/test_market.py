import random
import sys
from datetime import datetime, timedelta
from time import sleep

import configparser
import pytest
from decimal import Decimal
from pytezos import pytezos, Key

from src.accounts import Accounts
from src.config import Config
from src.market import Market

config = Config(config_file="tests/oracle.ini")

accounts = [
        {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"}
]

questions = [
        ["who", "why", "donald", 300, 50, 0.1, 0.2],
        ["who", "why", "donald", 300, 50, 1, 2],
]

expected = [
        []
]

test_data = [
    [accounts[0], questions[0]],
    [accounts[0], questions[1]]
]


def rand(mul=100):
    return random.randint(1,99) * mul


@pytest.mark.parametrize("accounts,data", test_data)
def test_fund_stablecoin(account, market, data, stablecoin_storage):
    market.transfer_stablecoin_to_user(account["name"], rand())
    sleep(3)
    balance = stablecoin_storage[account["key"]]()
    amount = rand(3000)
    market.transfer_stablecoin_to_user(account["name"], amount)
    sleep(3)
    new_balance = stablecoin_storage[account["key"]]()
    assert stablecoin_storage[account["key"]]()
    assert balance["balance"] + amount == new_balance["balance"]


@pytest.mark.parametrize("account,data", test_data)
def test_ask_question(account, market, data, questions_storage):
    auction_end = datetime.timestamp(datetime.now() + timedelta(minutes=data[5]))
    market_close = datetime.timestamp(datetime.now() + timedelta(minutes=data[6]))
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(3)
    question = questions_storage[ipfs_hash]()
    assert question['total_auction_quantity'] == data[3]
    assert question['state'] == "questionAuctionOpen"
    assert question['owner'] == account["key"]
    assert question['auction_end'] == int(auction_end)
    assert question['market_close'] == int(market_close)


@pytest.mark.parametrize("account,data", test_data)
def test_bid_auction(account, market, data, questions_storage):
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(3)
    question = questions_storage[ipfs_hash]()
    market.bid_auction(ipfs_hash, account["name"], 100, 10)
    sleep(3)
    bids = question["auction_bids"]
    assert account["key"] in bids


@pytest.mark.parametrize("account,data", test_data)
def test_close_auction(account, market, data, questions_storage):
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(data[5] * 60 + 60)
    market.close_auction(ipfs_hash, account["name"])
    sleep(3)
    question = questions_storage[ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionAuctionWithdrawOpen"


@pytest.mark.parametrize("account,data", test_data)
def test_close_market(account, market, data, questions_storage):
    sleep(3)
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(data[6] * 60 + 60)
    market.close_market(ipfs_hash, True, account["name"])
    sleep(3)
    question = questions_storage[ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionMarketClosed"

"""
@pytest.mark.parametrize("account,data", test_data)
def test_buy_token(account,market,data, stablecoin_storage):
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(2)
    balance = stablecoin_storage[account["key"]]()
    amount = rand(5)
    market.buy_token(ipfs_hash, True, amount, account["name"])
    sleep(2)
    new_balance = stablecoin_storage[account["key"]]()
    assert stablecoin_storage[account["key"]]()
    assert balance["balance"] - amount == new_balance["balance"]

@pytest.mark.parametrize("account,data", test_data)
def test_burn_token(account, market, data, stablecoin_storage):
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(2)
    market.bid_auction(ipfs_hash, account["name"], 100, 10)
    sleep(1)
    amount = 1000
    balance = stablecoin_storage[account["key"]]()
    market.burn(ipfs_hash, amount, account["name"])
    sleep(2)
    new_balance = [account["key"]]()
    assert stablecoin_storage[account["key"]]()
    assert balance["balance"] == new_balance["balance"] + amount
"""

