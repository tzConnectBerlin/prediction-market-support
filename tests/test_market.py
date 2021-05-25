import random
import sys
from datetime import datetime, timedelta
from time import sleep

import pytest
from loguru import logger

from src.utils import print_error, submit_transaction

from .conftest import get_random_market

MULTIPLIER = 10 ** 5

#accounts used for test
accounts = [
    {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"},
    #{"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3"}
]

#questions data to test functions
questions = [
    ["who", "why", "donald", 300 * MULTIPLIER, random.randint(0, 2 * 63), 0.1],
    #["who", "why", "mala", 300, 50 * MULTIPLIER, random.randint(0, 2 * 63), 1.1],
]

#testdata mix for easier use a parametrised
test_data = [
    [accounts[0], questions[0]],
    #[accounts[1], questions[1]],
]


def rand(mul=100):
    return random.randint(1, 99) * mul


@pytest.mark.parametrize("account,data", test_data)
def test_ask_question(account, market, data, questions_storage, stablecoin_id):
    market_id, transaction = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
    auction_end = datetime.timestamp(datetime.now() + timedelta(minutes=data[5]))
    submit_transaction(transaction, error_func=print_error)
    question = questions_storage[market_id]()
    metadata = question['metadata']
    assert 'auctionRunning' in question['state']
    state = question['state']['auctionRunning']
    assert data[0] in metadata['description']
    assert data[1] in metadata['description']
    assert metadata['adjudicator'] == account["key"]
    assert metadata['currency'] == {'fa12': stablecoin_id}
    assert abs(state['auction_period_end'] - int(auction_end)) <= 1
    assert state['quantity'] == data[3]
    sleep(2)

"""
@pytest.mark.parametrize("account", accounts)
def test_bid_auction(account, market, liquidity_storage):
    auction = get_random_market('created')
    amount = rand(100)
    rate = random.randint(0, 2 ** 63)
    transaction = market.bid_auction(auction['id'], account["name"], amount, rate)
    submit_transaction(transaction, error_func=print_error)
    sleep(2)
    key = {'originator': account['key'], 'market_id': auction['id']}
    bids = liquidity_storage[key]()
    assert bids['bet'] is not None
    assert bids['bet']['quantity'] >= amount


@pytest.mark.parametrize("data", questions)
def test_mutiple_bids(market, data, liquidity_storage, revealed_accounts):
    auction = get_random_market('created')
    amount = rand(100)
    rate = random.randint(0, 2 ** 63)
    logger.debug(auction)
    transaction = market.multiple_bids(auction['id'], amount, rate)
    submit_transaction(transaction, error_func=print_error)
    sleep(2)
    logger.debug(market.accounts.names())
    for r_account in revealed_accounts:
        key = {'originator': r_account['key'], 'market_id': auction['id']}
        bids = liquidity_storage[key]()
        assert bids['bet'] is not None
        assert bids['bet']['quantity'] >= amount


@pytest.mark.parametrize("account,data", test_data)
def test_auction_clear(account, market, data, questions_storage):
    auction = get_random_market('bidded')
    transaction = market.auction_clear(auction['id'], auction["caller_name"])
    submit_transaction(transaction, error_func=print_error)
    sleep(2)
    question = questions_storage[auction['id']]()
    auction_state = question['state']
    assert 'marketBootstrapped' in auction_state
    assert auction_state['marketBootstrapped']['resolution'] is None


@pytest.mark.parametrize("account,data", test_data)
def test_auction_withdraw(account, market, data, liquidity_storage):
    auction = get_random_market('cleared')
    logger.error(auction)
    transaction = market.auction_withdraw(auction["id"], account["name"])
    submit_transaction(transaction, error_func=print_error)
    sleep(2)
    key = {'originator': account['key'], 'market_id': auction['id']}
    bids = liquidity_storage[key]()
    logger.debug(bids)
    assert False


@pytest.mark.parametrize("account,data", test_data)
def test_close_market_yes(account, market, data, questions_storage):
    auction = get_random_market('cleared')
    transaction = market.close_market(auction["id"], auction["caller_name"], True)
    submit_transaction(transaction, error_func=print_error)
    sleep(2)
    question = questions_storage[auction['id']]()
    auction_state = question["state"]["marketBootstrapped"]
    assert auction_state['resolution']['winning_prediction'] == 'yes'


@pytest.mark.parametrize("account,data", test_data)
def test_close_market_no(account, market, data, questions_storage):
    auction = get_random_market('cleared')
    transaction = market.close_market(auction["id"], auction["caller_name"], False)
    submit_transaction(transaction, error_func=print_error)
    sleep(2)
    question = questions_storage[auction['id']]()
    auction_state = question["state"]["marketBootstrapped"]
    assert auction_state['resolution']['winning_prediction'] == 'no'


@pytest.mark.parametrize("account,data", test_data)
def test_market_enter_exist_payin(account, market, data, stablecoin, supply_storage):
    auction = get_random_market('cleared')
    amount = rand(100)
    stablecoin.fund(account["name"], amount)
    balance = supply_storage[(auction['id'] << 3) + 1]()
    transaction = market.market_enter_exit(auction["id"], account['name'], 'payIn', 2**6)
    submit_transaction(transaction, error_func=print_error)
    sleep(2)
    new_balance = supply_storage[(auction['id'] << 3) + 1]()
    assert balance != new_balance


@pytest.mark.parametrize("account,data", test_data)
def test_mint_token(account, market, data, stablecoin, supply_storage):
    auction = get_random_market('cleared')
    amount = rand(100)
    stablecoin.fund(account["name"], amount)
    balance = supply_storage[(auction['id'] << 3) + 1]()
    transaction = market.burn(auction['id'], account["name"], amount)
    submit_transaction(transaction, error_func=print_error)
    sleep(2)
    transaction = market.mint(auction['id'], account["name"], amount)
    submit_transaction(transaction, error_func=print_error)
    sleep(2)
    balance2 = supply_storage[(auction['id'] << 3) + 1]()
    assert balance2['total_supply'] == balance['total_supply']


@pytest.mark.parametrize("account,data", test_data)
def test_burn_token(account, market, data, stablecoin, supply_storage):
    auction = get_random_market('cleared')
    amount = rand(100)
    stablecoin.fund(account["name"], amount)
    balance = supply_storage[(auction['id'] << 3) + 1]()
    transaction = market.burn(auction['id'], account["name"], amount)
    submit_transaction(transaction, error_func=print_error)
    sleep(2)
    balance2 = supply_storage[(auction['id'] << 3) + 1]()
    assert balance2['total_supply'] > balance['total_supply']


@pytest.mark.parametrize("account,data", test_data)
def test_swap_tokens(account, market, data, liquidity_storage):
    auction = get_random_market('cleared')
    key = {'originator': account['key'], 'market_id': auction['id']}
    balance = liquidity_storage(key)
    transaction = market.swap_tokens(auction['id'], account["name"], "yes", 150)
    submit_transaction(transaction, error_func=print_error)
    sleep(2)
    new_balance = liquidity_storage[key]()
    assert new_balance['total_supply'] != balance['total_supply']


@pytest.mark.parametrize("account,data", test_data)
def test_update_liquidity(account, market, data, liquidity_storage):
    auction = get_random_market('cleared')
    amount = rand(100)
    key = {'originator': account['key'], 'market_id': auction['id']}
    liquidity = liquidity_storage[key]()
    logger.debug(liquidity)
    transaction = market.update_liquidity(auction['id'], account["name"], "payIn", amount)
    submit_transaction(transaction, error_func=print_error)
    market.update_liquidity(auction['id'], account["name"], "payOut", amount)
    sleep(2)
    liquidity = liquidity_storage[key]()
    logger.debug(liquidity)
    assert False
"""