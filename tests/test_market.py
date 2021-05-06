import random
import sys
from datetime import datetime, timedelta
from time import sleep


import pytest

MULTIPLIER = 10 ** 6

#accounts used for test
accounts = [
    {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"},
    {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3"}
]

#questions data to test functions
questions = [
    ["who", "why", "donald", 300 * MULTIPLIER, random.randint(0, 2 * 63), 0.1],
    ["who", "why", "mala", 300, 50 * MULTIPLIER, random.randint(0, 2 * 63), 1.1],
]

#testdata mix for easier use a parametrised
test_data = [
    [accounts[0], questions[0]],
    [accounts[1], questions[1]],
]


def rand(mul=100):
    return random.randint(1, 99) * mul


@pytest.mark.parametrize("account,data", test_data)
def test_ask_question(account, market, data, questions_storage, stablecoin_id):
    auction_end = datetime.timestamp(datetime.now() + timedelta(minutes=data[5]))
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(3)
    question = questions_storage[market_id]()
    metadata = question['metadata']
    assert 'auctionRunning' in question['state']
    state = question['state']['auctionRunning']
    assert data[0] in metadata['description']
    assert data[1] in metadata['description']
    assert metadata['adjudicator'] == account["key"]
    assert metadata['currency'] == {'fa12': stablecoin_id}
    assert state['auction_period_end'] == int(auction_end)
    assert state['quantity'] == data[3]


@pytest.mark.parametrize("account,data", test_data)
def test_bid_auction(account, market, data, liquidity_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(3)
    amount = rand(100)
    rate = random.randint(0, 2 ** 63)
    market.bid_auction(market_id, account["name"], amount, rate)
    sleep(3)
    key = {'originator': account['key'], 'market_id': market_id}
    bids = liquidity_storage[key]()
    assert bids['bet'] is not None
    assert bids['bet']['quantity'] >= amount


@pytest.mark.parametrize("account,data", test_data)
def test_auction_clear(account, market, data, questions_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(90 + 90)
    amount = rand(100)
    rate = random.randint(0, 2 ** 63)
    market.bid_auction(market_id, account["name"], amount, rate)
    sleep(9)
    market.auction_clear(market_id, account["name"])
    sleep(9)
    question = questions_storage[market_id]()
    auction_state = question['state']
    assert 'marketBootstrapped' in auction_state
    assert auction_state['marketBootstrapped']['resolution'] is None

@pytest.mark.parametrize("account,data", test_data)
def test_auction_withdraw(account, market, data, questions_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(90 + 90)
    amount = rand(100)
    rate = random.randint(0, 2 ** 63)
    market.bid_auction(market_id, account["name"], amount, rate)
    sleep(9)
    market.auction_clear(market_id, account["name"])
    sleep(3)
    market.auction_withdraw(market_id, account["name"])
    question = questions_storage[market_id]()
    auction_state = question["state"]
    print(auction_state)
    sleep(2)


@pytest.mark.parametrize("account,data", test_data)
def test_close_market_yes(account, market, data, questions_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(9)
    amount = rand(100)
    rate = random.randint(0, 2 ** 63)
    market.bid_auction(market_id, account["name"], amount, rate)
    sleep(60 + 60)
    market.auction_clear(market_id, account["name"])
    sleep(9)
    market.close_market(market_id, account["name"], True)
    sleep(3)
    question = questions_storage[market_id]()
    auction_state = question["state"]["marketBootstrapped"]
    assert 'yes' in auction_state['resolution']


@pytest.mark.parametrize("account,data", test_data)
def test_close_market_no(account, market, data, questions_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(9)
    amount = rand(100)
    rate = random.randint(0, 2 ** 63)
    market.bid_auction(market_id, account["name"], amount, rate)
    sleep(60 + 60)
    market.auction_clear(market_id, account["name"])
    sleep(9)
    market.close_market(market_id, account["name"], False)
    sleep(3)
    question = questions_storage[market_id]()
    auction_state = question["state"]["marketBootstrapped"]
    assert 'no' in auction_state['resolution']


@pytest.mark.parametrize("account,data", test_data)
def test_market_enter_exist_payin(account, market, data, liquidity_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(9)
    market.auction_clear(market_id, account['name'])
    sleep(60 * 60)
    market.market_enter_exit(market_id, account['name'], 'payIn', 100)
    sleep(3)
    key = {'originator': account['key'], 'market_id': market_id}
    bids = liquidity_storage[key]
    print(bids)
    assert False


@pytest.mark.parametrize("account,data", test_data)
def test_mint_token(account, market, data, supply_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(60 * 60)
    market.auction_clear(market_id, account["name"])
    sleep(9)
    amount = rand(100)
    balance = supply_storage[(market_id << 3) + 0]()
    market.mint(market_id, account["name"], amount)
    sleep(9)
    balance2 = supply_storage[(market_id << 3) + 0]()
    assert balance2 > balance


@pytest.mark.parametrize("account,data", test_data)
def test_burn_token(account, market, data, supply_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(60 * data[5] + 20)
    market.auction_clear(market_id, account["name"])
    sleep(9)
    amount = rand(100)
    balance = supply_storage[(market_id << 3) + 0]()
    market.burn(market_id, account["name"], amount)
    sleep(9)
    balance2 = supply_storage[(market_id << 3) + 0]()
    assert balance2 < balance


@pytest.mark.parametrize("account,data", test_data)
def test_swap_tokens(account, market, data, supply_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(9)
    amount = rand(100)
    rate = random.randint(0, 2 ** 63)
    market.bid_auction(market_id, account["name"], amount, rate)
    sleep(60 * data[5] + 20)
    market.auction_clear(market_id, account["name"])
    sleep(9)
    balance = supply_storage[(market_id << 3) + 1]()
    market.swap_tokens(market_id, account["name"], "yes", 150)
    sleep(9)
    new_balance = supply_storage[(market_id << 3) + 1]()
    assert new_balance > balance


@pytest.mark.parametrize("account,data", test_data)
def test_update_liquidity(account, market, data, supply_storage):
    market_id = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    sleep(60 * data[5] + 20)
    market.auction_clear(market_id, account["name"])
    sleep(9)
    amount = rand(1000)
    balance = supply_storage[account["key"]]()
    market.update_liquidity(market_id, account["name"], "payIn", amount)
    new_balance1 = supply_storage[account["key"]]()
    market.update_liquidity(market_id, account["name"], "payOut", amount)
    sleep(2)
    new_balance2 = supply_storage[account["key"]]()
    assert balance < new_balance1
    assert new_balance1 < new_balance2

#swapToken
#swapLiquidity
#claimWinnings