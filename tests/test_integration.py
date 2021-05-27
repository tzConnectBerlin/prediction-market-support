import sys
from datetime import datetime, timedelta
from time import sleep

import pytest
from pytezos.rpc.node import RpcError
from loguru import logger

from src.utils import submit_transaction, print_error, raise_error
from .conftest import get_random_market


""""
def test_create_market_correct_bet_success_fa12(stablecoin_id, market, questions_storage, liquidity_storage):
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        "donald",
        quantity,
        2**32,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=stablecoin_id
    )
    log_and_submit(
        transaction,
        {'name': 'donald', 'key': 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2'},
        market,
        "create_market",
        {},
        market_id
    )
    sleep(1)
    storage = questions_storage[market_id]()
    metadata = storage['metadata']
    state = storage['state']
    map_key = {'originator': 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2', 'market_id': market_id}
    liquidity = liquidity_storage[map_key]()
    assert metadata['adjudicator'] == 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2'
    assert 'auctionRunning' in state
    assert state['auctionRunning']['quantity'] == quantity
    ### yes_preference should be probability * quantity
    assert state['auctionRunning']['yes_preference'] == (2**32 * quantity)
    assert state['auctionRunning']['uniswap_contribution'] == (2**32 * quantity)
    assert liquidity['bet']['quantity'] == quantity
    assert int(liquidity['bet']['predicted_probability']) == int(2**32)

#test_create_market_correct_bet_success_fa2
"""


def test_create_market_non_existent_currency(market):
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    _market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        "donald",
        1000,
        2**32,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract="KT1VKHPi2rWsRGPpZ6WpNxrKGtGA1LRcgFAp"
    )
    with pytest.raises(RpcError):
        submit_transaction(transaction, error_func=raise_error)


@pytest.mark.parametrize("quantity,rate", [[0, 2**34], [1000, 2*65]])
def test_create_market_incorrect_bet(stablecoin_id, market, quantity, rate):
    end = datetime.now() + timedelta(minutes=5)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        "donald",
        quantity,
        rate,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=stablecoin_id
    )
    with pytest.raises(RpcError):
        logger.debug(f'{quantity} {rate}')
        submit_transaction(transaction, error_func=raise_error)


#test_create_market_currency_balance_FA12

def test_create_market_already_used_market_id(stablecoin_id, market, gen_markets):
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    market_id = get_random_market()
    _market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        "donald",
        quantity,
        2**32,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=market_id['id'],
        token_contract=stablecoin_id
    )
    with pytest.raises(RpcError):
        submit_transaction(transaction, error_func=raise_error)


def test_auction_bet_new_address_correct_bet(market, liquidity_storage, gen_markets):
    auction = get_random_market("created")
    quantity = 1000
    rate = 2**32
    operation = market.bid_auction(auction['id'], "mala", quantity, rate)
    submit_transaction(operation, error_func=raise_error)
    storage = market.get_storage(auction['id'], "mala")
    bet = storage['liquidity_provider_map']["bet"]
    assert bet['quantity'] == quantity
    assert bet['predicted_probability'] == rate
    #uniswap contribution and yes_preference to check


def test_auction_bet_existing_address_correct_bet(market, gen_bid_markets):
    auction = get_random_market("bidded")
    quantity = 1000
    rate = 2**32
    operation = market.bid_auction(auction['id'], "mala", quantity, rate)
    submit_transaction(operation, error_func=raise_error)
    storage = market.get_storage(auction['id'], "mala")
    bet = storage['liquidity_provider_map']["bet"]
    assert bet['quantity'] == quantity
    assert bet['predicted_probability'] == rate
    #uniswap contribution and yes_preference to check


@pytest.mark.parametrize("quantity,rate,status", [
        [0, 2**34, 'created'],
        [1000, 2*65, 'created'],
        [1000, 2**32, 'cleared']
    ]
)
def test_auction_bet_existing_address_incorrect_bet(market, quantity, rate, status, gen_cleared_markets):
    auction = get_random_market(status)
    operation = market.bid_auction(auction['id'], "mala", quantity, rate)
    submit_transaction(operation, error_func=raise_error)
    storage = market.get_storage(auction['id'], "mala")
    bet = storage['liquidity_provider_map']["bet"]
    assert bet['quantity'] == quantity
    assert bet['predicted_probability'] == rate
    #uniswap contribution and yes_preference to check


#test_auction_bet_currency_balance_FA12


def test_auction_bet_non_existent_market_id(market):
    operation = market.bid_auction(1, "mala", 1000, 2*32)
    with pytest.raises(RpcError):
        submit_transaction(operation, error_func=raise_error)


def test_auction_bet_existing_address_incorrect_bet(market, gen_bid_markets):
    auction = get_random_market("bidded")
    operation = market.bid_auction(auction['id'], "mala", 1000, 2**32)
    with pytest.raises(RpcError):
        submit_transaction(operation, error_func=raise_error)


def test_clear_market_in_auction_phase(market, gen_bid_markets):
    auction = get_random_market("bidded")
    operation = market.auction_clear(auction['id'], auction['caller_name'])
    submit_transaction(operation, error_func=raise_error)
    storage = market.get_storage(auction['id'], auction['caller_name'])
    state = storage['market_map']['state']
    assert 'marketBootstrapped' in state
    assert 'auctionRunning' not in state
    assert state['marketBootstrapped']['resolution'] is None
    #check if the uniswap pool and check the contribution factor for each user

