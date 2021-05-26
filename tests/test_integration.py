from datetime import datetime, timedelta
from time import sleep

import pytest
from pytezos.rpc.node import RpcError
from loguru import logger

from src.utils import submit_transaction, print_error, raise_error


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
    submit_transaction(transaction, error_func=print_error)
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


def test_create_market_correct_bet_success_fa12(stablecoin_id, market, questions_storage, liquidity_storage):
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



@pytest.mark.parametrize("quantity,rate", [[0, 2**34], [1000, 0]])
def test_create_market_incorrect_bet(stablecoin_id, market, questions_storage, liquidity_storage, quantity, rate):
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
    #with pytest.raises(RpcError):
    submit_transaction(transaction, error_func=raise_error)

