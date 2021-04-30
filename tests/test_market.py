import random
from datetime import datetime, timedelta
from time import sleep


import pytest

import src.utils as utils

#accounts used for test
accounts = [
    {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"},
    {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3"}
]

#questions data to test functions
questions = [
    ["who", "why", "donald", 300, 50, 0.1, 0.2],
    ["who", "why", "mala", 300, 50, 1, 2],
]

#testdata mix for easier use a parametrised
test_data = [
    [accounts[0], questions[0]],
    [accounts[1], questions[1]],
]


def rand(mul=100):
    return random.randint(1, 99) * mul


@pytest.mark.parametrize("account,data", test_data)
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
def test_ask_question(account, market, data, questions_storage, stablecoin_id):
    auction_end = datetime.timestamp(datetime.now() + timedelta(minutes=data[5]))
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(3)
    question = questions_storage[market_id]()
    metadata = question['metadata']
    assert 'auctionRunning' in question['state']
    state = question['state']['auctionRunning']
    assert metadata['total_auction_quantity'] == data[3]
    assert metadata['description'] == data[0] + data[1]
    assert metadata['adjudicator'] == account["key"]
    assert metadata['currency'] == {'FA12': stablecoin_id}
    assert state['auction_period_end'] == int(auction_end)
    assert state['quantity'] == data[3]


@pytest.mark.parametrize("account,data", test_data)
def test_bid_auction(account, market, data, liquidity_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(3)
    market.bid_auction(market_id, account["name"], 100, 10)
    sleep(3)
    ledger = liquidity_storage[market_id]()
    key = {'originator': account['key'], 'market_id': market_id}
    assert key in ledger
    bids = ledger[key]
    assert 'bet' in bids
    assert bids['bet']['quantity'] == 100


"""
@pytest.mark.parametrize("account,data", test_data)
def test_close_auction(account, market, data, questions_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(data[5] * 60 + 60)
    market.close_auction(market_id, account["name"])
    sleep(3)
    question = questions_storage[market_id]()
    auction_state = question["state"]
    assert auction_state == "questionAuctionWithdrawOpen"


@pytest.mark.parametrize("account,data", test_data)
def test_close_market(account, market, data, questions_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(data[6] * 60 + 60)
    market.close_market(market_id, True, account["name"])
    sleep(3)
    question = questions_storage[market_id]()
    auction_state = question["state"]
    assert auction_state == "questionMarketClosed"


@pytest.mark.parametrize("account,data", test_data)
def test_buy_token(account, market, data, stablecoin_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(2)
    balance = stablecoin_storage[account["key"]]()
    amount = rand(10000000)
    market.buy_token(market_id, True, amount, account["name"])
    sleep(2)
    new_balance = stablecoin_storage[account["key"]]()
    assert stablecoin_storage[account["key"]]()
    assert balance["balance"] - amount == new_balance["balance"]


@pytest.mark.parametrize("account,data", test_data)
def test_burn_token(account, market, data, stablecoin_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(2)
    amount = rand(90)
    balance = stablecoin_storage[account["key"]]()
    market.burn(market_id, amount, account["name"])
    sleep(2)
    new_balance = [account["key"]]()
    assert stablecoin_storage[account["key"]]()
    assert balance["balance"] == new_balance["balance"] + amount


@pytest.mark.parametrize("account,data", test_data)
def test_update_liquidity(account, market, data, stablecoin_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(2)
    balance = stablecoin_storage[account["key"]]()
    amount = rand(1000)
    market.update_liquidity(market_id, True, amount, account["name"])
    sleep(2)
    new_balance1 = stablecoin_storage[account["key"]]()
    market.update_liquidity(market_id, False, amount, account['name'])
    sleep(2)
    new_balance2 = stablecoin_storage[account["key"]]()
    assert balance < new_balance1
    assert new_balance1 < new_balance2


@pytest.mark.parametrize("account,data", test_data)
def test_withdraw_auction(account, market, data, stablecoin_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(2)
"""
