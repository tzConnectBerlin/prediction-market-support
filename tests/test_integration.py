from src.market import Market
from time import sleep

import pytest
from loguru import logger

from src.utils import submit_transaction, print_error


def test_create_market_correct_bet_success_fa12(stablecoin_id, market, questions_storage, liquidity_storage):
    quantity = 1000
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        "donald",
        1000,
        2**32,
        "dededede",
        auction_end_date="in 5 minute",
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


# my_market = Market()
# my_market.get_storage()