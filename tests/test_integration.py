import sys
from datetime import datetime, timedelta
from time import sleep

import pytest
from pytezos.rpc.node import RpcError
from loguru import logger

from src.utils import log_and_submit, raise_error
from .conftest import get_random_market


def test_create_market_correct_bet_success_fa12(
        stablecoin_id,
        market,
        questions_storage,
        liquidity_storage,
        revealed_account):
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        revealed_account["name"],
        quantity,
        2**32,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=stablecoin_id
    )
    log_and_submit(
        transaction,
        revealed_account,
        market,
        market_id=market_id
    )
    sleep(3)
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

''' 
def test_create_market_non_existent_currency(market, revealed_account):
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        revealed_account['name'],
        quantity,
        2**32,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract="KT1VKHPi2rWsRGPpZ6WpNxrKGtGA1LRcgFAp"
    )
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, market_id, error_func=raise_error)


@pytest.mark.parametrize("quantity,rate", [[0, 2**34], [1000, 2*65]])
def test_create_market_incorrect_bet(stablecoin_id, market, quantity, rate, revealed_account):
    end = datetime.now() + timedelta(minutes=5)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        revealed_account['name'],
        quantity,
        rate,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=stablecoin_id
    )
    with pytest.raises(RpcError):
        logger.debug(f'{quantity} {rate}')
        log_and_submit(transaction, revealed_account, market, market_id, error_func=raise_error)


#test_create_market_currency_balance_FA12

def test_create_market_already_used_market_id(stablecoin_id, market, gen_markets, revealed_account):
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    auction = get_random_market()
    transaction = market.ask_question(
        "when",
        "tomorrow",
        revealed_account['name'],
        quantity,
        2**32,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=auction['id'],
        token_contract=stablecoin_id
    )
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], auction["id"], error_func=raise_error)


def test_auction_bet_new_address_correct_bet(market, liquidity_storage, gen_markets, revealed_account):
    auction = get_random_market("created")
    quantity = 1000
    rate = 2**32
    transaction = market.bid_auction(auction['id'], revealed_account['name'], quantity, rate)
    log_and_submit(transaction, auction['caller'], auction["id"], error_func=raise_error)
    storage = market.get_storage(auction['id'], revealed_account['name'])
    bet = storage['liquidity_provider_map']['bet']
    assert bet['quantity'] == quantity
    assert bet['predicted_probability'] == rate
    #uniswap contribution and yes_preference to check


def test_auction_bet_existing_address_correct_bet(market, gen_bid_markets, revealed_account):
    auction = get_random_market("bidded")
    quantity = 1000
    rate = 2**32
    transaction = market.bid_auction(auction['id'], revealed_account["name"], quantity, rate)
    log_and_submit(transaction, auction['caller'], auction["id"], error_func=raise_error)
    storage = market.get_storage(auction['id'], revealed_account['name'])
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
def test_auction_bet_existing_address_incorrect_bet(market, quantity, rate, status, gen_cleared_markets, revealed_account):
    auction = get_random_market(status)
    transaction = market.bid_auction(auction['id'], revealed_account['name'], quantity, rate)
    log_and_submit(transaction, auction['caller'], auction["id"], error_func=raise_error)
    storage = market.get_storage(auction['id'], revealed_account['name'])
    bet = storage['liquidity_provider_map']["bet"]
    assert bet['quantity'] == quantity
    assert bet['predicted_probability'] == rate
    #uniswap contribution and yes_preference to check


#test_auction_bet_currency_balance_FA12


def test_auction_bet_non_existent_market_id(market, revealed_account):
    transaction = market.bid_auction(1, revealed_account['name'], 1000, 2*32)
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, 1, error_func=raise_error)


def test_clear_market_in_auction_phase(market, gen_bid_markets, revealed_account):
    auction = get_random_market("bidded")
    transaction = market.auction_clear(auction['id'], auction['caller']['name'])
    log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)
    storage = market.get_storage(auction['id'], auction['caller']['name'])
    state = storage['market_map']['state']
    assert 'marketBootstrapped' in state
    assert 'auctionRunning' not in state
    assert state['marketBootstrapped']['resolution'] is None
    #check if the uniswap pool and check the contribution factor for each user


def test_clear_market_in_auction_phase(market, gen_bid_markets, revealed_account):
    auction = get_random_market("cleared")
    transaction = market.auction_clear(auction['id'], auction['caller']['name'])
    storage = market.get_storage(auction['id'], auction['caller']['name'])
    state = storage['market_map']['state']
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)
    #check if the uniswap pool and check the contribution factor for each user


def test_clear_non_existent_market_id(market, gen_bid_markets, revealed_account):
    transaction = market.auction_clear(1, revealed_account['name'])
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, 1, error_func=raise_error)


def test_mint_token_on_cleared(market, gen_resolved_market, revealed_account):
    auction = get_random_market("cleared")
    transaction = market.mint(auction['id'], auction['caller']['name'], 100)


def test_mint_token_in_auction_phase(market, gen_resolved_market, revealed_account):
    auction = get_random_market("cleared")
    transaction = market.mint(auction['id'], auction['caller']['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_mint_resolved_market(market, gen_resolved_market, revealed_account):
    auction = get_random_market("resolved")
    transaction = market.mint(auction['id'], auction['caller']['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_burn_inexistent_market(market, gen_resolved_market, revealed_account):
    auction = get_random_market("resolved")
    transaction = market.burn(1, auction['caller']['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_burn_token_on_cleared(market, gen_resolved_market, revealed_account):
    auction = get_random_market("cleared")
    transaction = market.burn(auction['id'], auction['caller']['name'], 100)


def test_burn_token_in_auction_phase(market, gen_resolved_market, revealed_account):
    auction = get_random_market("bidded")
    transaction = market.burn(auction['id'], auction['caller']['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_burn_resolved_market(market, gen_resolved_market, revealed_account):
    auction = get_random_market("resolved")
    transaction = market.burn(auction['id'], auction['caller']['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_burn_inexistent_market(market):
    auction = get_random_market("resolved")
    transaction = market.burn(1, auction['caller']['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], 1, error_func=raise_error)


def test_swap_token_token_on_cleared(market, gen_resolved_market, revealed_account):
    auction = get_random_market("cleared")
    transaction = market.swap_tokens(auction['id'], auction['caller']['name'], "yes", 100)


def test_swap_token_token_in_auction_phase(market, gen_cleared_markets, revealed_account):
    auction = get_random_market("bidded")
    transaction = market.swap_tokens(auction['id'], auction['caller']['name'], "yes", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_swap_token_resolved_market(market, gen_resolved_market, revealed_account):
    auction = get_random_market("resolved")
    transaction = market.swap_tokens(auction['id'], auction['caller']['name'], "yes", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_swap_token_inexistent_market(market, gen_resolved_market, revealed_account):
    auction = get_random_market("resolved")
    transaction = market.swap_tokens(auction['id'], auction['caller']['name'], "yes", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_add_liquidity_on_cleared(market, gen_cleared_markets, revealed_account):
    auction = get_random_market("cleared")
    transaction = market.update_liquidity(auction['id'], auction['caller']['name'], "payIn", 100)


def test_add_liquidity_in_auction_phase(market, gen_cleared_markets, revealed_account):
    auction = get_random_market("cleared")
    transaction = market.update_liquidity(auction['id'], auction['caller']['name'], "payIn", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_add_liquidity_resolved_market(market, gen_resolved_market, revealed_account):
    auction = get_random_market("resolved")
    transaction = market.update_liquidity(auction['id'], auction['caller']['name'], "payIn", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_add_liquidity_inexistent_market(market, revealed_account):
    transaction = market.update_liquidity(1, revealed_account['name'], "payIn", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, 1, error_func=raise_error)


def test_remove_liquidity_on_cleared(market, gen_cleared_markets, revealed_account):
    auction = get_random_market("cleared")
    transaction = market.update_liquidity(auction['id'], auction['caller']['name'], "payOut", 100)


def test_remove_liquidity_in_auction_phase(market, gen_bid_markets):
    auction = get_random_market("bidded")
    transaction = market.update_liquidity(auction['id'], auction['caller']['name'], "payOut", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_remove_liquidity_resolved_market(market, gen_resolved_market):
    auction = get_random_market("resolved")
    transaction = market.update_liquidity(auction['id'], auction['caller']['name'], "payOut", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


def test_remove_liquidity_inexistent_market(market):
    auction = get_random_market("created")
    transaction = market.update_liquidity(1, auction['caller']['name'], "payOut", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, 1, error_func=raise_error)


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_in_cleared_phase(market, gen_bid_markets, revealed_account, token_type):
    auction = get_random_market("cleared")
    transaction = market.close_market(auction['id'], auction['caller']['name'])
    log_and_submit(transaction, auction['caller'], market, auction['id'], error_func=raise_error)
    storage = market.get_storage(auction['id'], auction['caller']['name'])
    state = storage['market_map']['state']
    assert 'marketBootstrapped' in state
    assert 'auctionRunning' not in state
    assert state['marketBootstrapped']['resolution'] is not None


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_in_auction_phase(market, gen_bid_markets, revealed_account, token_type):
    auction = get_random_market("bidded")
    transaction = market.close_market(auction['id'], auction['caller']['name'], token_type)
    log_and_submit(transaction, auction['caller'], market, auction['id'], error_func=raise_error)
    storage = market.get_storage(auction['id'], auction['caller']['name'])
    state = storage['market_map']['state']
    assert 'marketBootstrapped' in state
    assert 'auctionRunning' not in state
    assert state['marketBootstrapped']['resolution'] is not None


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_already_resolved(market, gen_bid_markets, revealed_account, token_type):
    auction = get_random_market("resolved")
    transaction = market.close_market(auction['id'], auction['caller']['name'], token_type)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_unauthorized_account(market, gen_bid_markets, revealed_account, token_type):
    auction = get_random_market("cleared")
    transaction = market.close_market(auction['id'], revealed_account['name'], token_type)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_non_existent_market_id(market, revealed_account, token_type):
    transaction = market.close_market(1, revealed_account['name'], token_type)
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, 1, error_func=raise_error)
'''
