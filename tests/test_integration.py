import random
from time import sleep
from datetime import datetime, timedelta

import pytest
from loguru import logger
from pytezos.rpc.node import RpcError

from src.utils import log_and_submit, raise_error
from src.utils import id_generator

LOGGING_RAISE = False

#exist to load fixtures and check how long the function takes
def test_empty():
    assert True


"""
Create Market
"""

def test_create_market_correct_bet_success_fa12(
        stablecoin_id,
        market
):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        caller["name"],
        quantity,
        2 ** 32,
        id_generator(15),
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=stablecoin_id
    )
    log_and_submit(
        transaction,
        caller,
        market,
        market_id=market_id
    )
    storage = market.get_storage(market_id, caller['name'])
    metadata = storage['market_map']['metadata']
    state = storage['market_map']['state']
    liquidity = storage['liquidity_provider_map']
    name = caller['name']
    assert metadata['adjudicator'] == caller['key']
    assert 'auctionRunning' in state
    assert state['auctionRunning']['quantity'] == quantity
    # yes_preference should be probability * quantity
    assert state['auctionRunning']['yes_preference'] == (2 ** 32 * quantity)
    assert state['auctionRunning']['uniswap_contribution'] == (2 ** 32 * quantity)
    assert liquidity[name]['bet']['quantity'] == quantity
    assert int(liquidity[name]['bet']['predicted_probability']) == int(2 ** 32)


# test_create_market_correct_bet_success_fa2

def test_create_market_non_existent_currency(market):
    quantity = 1000
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=5)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        caller['name'],
        quantity,
        2 ** 32,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract="KT1VKHPi2rWsRGPpZ6WpNxrKGtGA1LRcgFAp"
    )
    with pytest.raises(RpcError, match=r'Invalid external token contract'):
        log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=LOGGING_RAISE)


@pytest.mark.parametrize("quantity,rate, error", [
    [0, 2 ** 34, 'Amount must be greater than zero'],
    [1000, 2 ** 65, 'Probability must be a fixed point number with domain']
])
def test_create_market_incorrect_bet(stablecoin_id, market, quantity, rate, error):
    end = datetime.now() + timedelta(minutes=5)
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        caller['name'],
        quantity,
        rate,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=stablecoin_id
    )
    with pytest.raises(RpcError, match=rf'{error}'):
        logger.info(f'{quantity} {rate}')
        log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=LOGGING_RAISE)


def test_create_market_already_used_market_id(stablecoin_id, market):
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        caller['name'],
        quantity,
        2 ** 32,
        "dededede",
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=LOGGING_RAISE)
    sleep(1)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        caller['name'],
        quantity,
        2 ** 32,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=market_id,
        token_contract=stablecoin_id
    )
    with pytest.raises(RpcError, match=r'Market already exists'):
        log_and_submit(
            transaction, caller, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )
"""
Bet on Market 
"""


def test_auction_bet_new_address_correct_bet(market, stablecoin_id):
    rate = random.randint(1, 2 ** 63)
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        quantity,
        rate,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    logger.error(market_id)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    quantity = 1000
    rate = 2 ** 32
    caller2 = {"name": "marty", "key": "tz1Q3eT3kwr1hfvK49HK8YqPadNXzxdxnE7u", "status": "created"}
    sleep(4)
    transaction = market.bid_auction(market_id, caller2['name'], quantity, rate)
    logger.error(market_id)
    before_storage, after_storage = log_and_submit(transaction, caller2, market, market_id, error_func=raise_error, logging=True)
    name = caller2['name']
    bet = after_storage['liquidity_provider_map'][name]['bet']
    assert bet['quantity'] == quantity
    assert bet['predicted_probability'] == rate


def test_auction_bet_existing_address_correct_bet(market, stablecoin_id):
    rate = random.randint(1, 2 ** 63)
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        quantity,
        rate,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    rate = 2 ** 32
    sleep(2)
    transaction = market.bid_auction(market_id, caller['name'], quantity, rate)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    rate = 2 ** 41
    storage = market.get_storage(market_id, caller['name'])
    name = caller['name']
    bet = storage['liquidity_provider_map'][name]['bet']
    #3 bids at that quantity
    assert bet['quantity'] == quantity * 2
    #compute proper value here
    assert bet['predicted_probability'] != rate


@pytest.mark.parametrize("quantity,rate, error", [
    [0, 2 ** 34, 'Amount must be greater than zero'],
    [1000, 2 ** 65, 'Probability must be a fixed point number with domain']
])
def test_auction_incorrect_bet(market,  quantity, rate, error, stablecoin_id):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    better = {"name": "rimk", "key": "tz1PMqV7qGgWMNH2HR9inWjSvf3NwtHg7Xg4", "status": "created"}
    end = datetime.now() + timedelta(minutes=5)
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2**63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.bid_auction(market_id, better['name'], quantity, rate)
    with pytest.raises(RpcError, match=rf'{error}'):
        log_and_submit(transaction, better, market, market_id, error_func=raise_error)


def test_auction_bet_insufficient_currency_balance(market, stablecoin_id):
    quantity = 1000
    rate = 2 ** 32
    end = datetime.now() + timedelta(minutes=5)
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    attacker = {"name": "stavros", "key": "tz1iPFr4obPeSzknBPud8uWXZC7j5gKoah8d", "status": "created"}
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        quantity,
        rate,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, attacker, market, market_id, error_func=raise_error, logging=False)
    transaction = market.bid_auction(market_id, attacker['name'], quantity, rate)
    with pytest.raises(RpcError, match=r'NotEnoughBalance'):
        log_and_submit(
            transaction, attacker, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_auction_bet_non_existent_market_id(market):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    transaction = market.bid_auction(1, caller['name'], 1000, 2 * 32)
    with pytest.raises(RpcError, match=r'No such market'):
        log_and_submit(
            transaction, caller, market, 1, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_auction_bet_market_already_cleared(market, stablecoin_id):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    _before_storage, after_storage = log_and_submit(
        transaction,
        caller,
        market,
        market_id,
        error_func=raise_error
    )
    transaction = market.bid_auction(market_id, caller['name'], 1000, 2 * 32)
    with pytest.raises(RpcError, match=r'Market auction closed'):
        log_and_submit(
            transaction, caller, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )

"""
Clear market
"""


def test_clear_market_in_auction_phase(market, stablecoin_id):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.multiple_bids(market_id)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    _before_storage, after_storage = log_and_submit(
        transaction,
        caller,
        market,
        market_id,
        error_func=raise_error
    )
    state = after_storage['market_map']['state']
    assert 'marketBootstrapped' in state
    assert 'auctionRunning' not in state
    assert state['marketBootstrapped']['resolution'] is None



@pytest.mark.parametrize("quantity,rate", [[1, 100], [1, 2]])
def test_clear_market_insufficient_liquidity_from_bets(market, quantity, rate, stablecoin_id):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        quantity,
        rate,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    with pytest.raises(RpcError, match=r'Can\'t clear unhealthy market: no liquidity provided to'):
        log_and_submit(
            transaction, caller, market, market_id, error_func=raise_error, logging=True
        )


def test_clear_market_on_cleared(market, stablecoin_id):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    with pytest.raises(RpcError, match=r'Market auction closed'):
        log_and_submit(
            transaction, caller, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_clear_non_existent_market_id(market):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    transaction = market.auction_clear(1, caller['name'])
    with pytest.raises(RpcError, match=r'No such market'):
        log_and_submit(transaction, caller, market, 1, error_func=raise_error, logging=LOGGING_RAISE)

"""
Auction withdraw
"""


def test_withdraw_auction_cleared(market, stablecoin_id):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_withdraw(market_id, account["name"])
    before_storage, after_storage = log_and_submit(
        transaction,
        account,
        market,
        market_id,
        error_func=raise_error
    )


def test_withdraw_auction_bidded(market, stablecoin_id):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_withdraw(market_id, account["name"])
    with pytest.raises(RpcError, match=r'Market not bootstrapped'):
        log_and_submit(
            transaction, account, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )

def test_withdraw_auction_resolved(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.close_market(market_id, account['name'], True)
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_withdraw(market_id, account["name"])
    before_storage, after_storage = log_and_submit(
        transaction,
        account,
        market,
        market_id,
        error_func=raise_error
    )


def test_withdraw_without_participating_in_the_market(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    attacker = {"name": "marty", "key": "tz1Q3eT3kwr1hfvK49HK8YqPadNXzxdxnE7u", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_withdraw(market_id, attacker["name"])
    with pytest.raises(RpcError, match=r'(Caller has not provided liquidity or participated in the)'):
        log_and_submit(transaction, attacker, market, market_id, error_func=raise_error, logging=LOGGING_RAISE)

def test_withdraw_auction_non_existent_market_id(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    transaction = market.auction_withdraw(1, account['name'])
    with pytest.raises(RpcError, match=r'(No such market|Caller has not provided liquidity or participated in the)'):
        log_and_submit(transaction, account, market, 1, error_func=raise_error, logging=LOGGING_RAISE)


"""
Mint token
"""
import time
def test_mint_token_on_cleared(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)

    quantity = 100
    transaction = market.mint(market_id, account['name'], quantity)
    before_storage, after_storage = log_and_submit(
        transaction,
        account,
        market,
        market_id,
        error_func=raise_error
    )
    before_supply = before_storage["supply_map"]
    after_supply = after_storage["supply_map"]
    assert before_supply['no_token']['total_supply'] + quantity == after_supply['no_token']['total_supply']
    assert before_supply['yes_token']['total_supply'] + quantity == after_supply['yes_token']['total_supply']


def test_mint_token_in_auction_phase(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)

    transaction = market.mint(market_id, account['name'], 100)
    with pytest.raises(RpcError, match=r'Market not bootstrapped'):
        log_and_submit(
            transaction, account, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_mint_resolved_market(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.close_market(market_id, account['name'], True)
    log_and_submit(transaction, account, market, market_id, logging=True)

    transaction = market.mint(market_id, account['name'], 100)
    with pytest.raises(RpcError, match=r'Market has already been resolved'):
        log_and_submit(
            transaction, account, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_mint_inexistent_market(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    transaction = market.mint(1, account['name'], 100)
    with pytest.raises(RpcError, match=r'No such market'):
        log_and_submit(transaction, account, market, 1, error_func=raise_error, logging=LOGGING_RAISE)


def test_mint_insufficient_currency_balance(market, stablecoin):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    attacker = {"name": "leonidas", "key": "tz1ZrWi7V8tu3tVepAQVAEt8jgLz4VVEEf7m", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)
    
    transaction = market.mint(market_id, attacker['name'], 100)
    with pytest.raises(RpcError, match=r'NotEnoughBalance'):
        log_and_submit(
            transaction, attacker, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )
    


"""
Burn token
"""


def test_burn_token_on_cleared(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)

    quantity = 100
    
    transaction = market.mint(market_id, account['name'], quantity)
    before_storage, after_storage = log_and_submit(
        transaction,
        account,
        market,
        market_id,
        error_func=raise_error
    )
    transaction = market.burn(market_id, account['name'], quantity)
    before_storage, after_storage = log_and_submit(
        transaction,
        account,
        market,
        market_id,
        error_func=raise_error
    )
    before_supply = before_storage["supply_map"]
    after_supply = after_storage["supply_map"]
    assert before_supply['no_token']['total_supply'] - quantity == after_supply['no_token']['total_supply']
    assert before_supply['yes_token']['total_supply'] - quantity == after_supply['yes_token']['total_supply']


def test_burn_token_in_auction_phase(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.burn(market_id, account['name'], 100)
    with pytest.raises(RpcError, match=r'Market not bootstrapped'):
        log_and_submit(
            transaction, account, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_burn_resolved_market(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.close_market(market_id, account['name'], True)
    log_and_submit(transaction, account, market, market_id, logging=True)
    
    transaction = market.burn(market_id, account['name'], 100)
    with pytest.raises(RpcError, match=r'Market has already been resolved'):
        log_and_submit(
            transaction, account, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_burn_inexistent_market(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    transaction = market.burn(1, account['name'], 100)
    with pytest.raises(RpcError, match=r'No such market'):
        log_and_submit(transaction, account, market, 1, error_func=raise_error, logging=LOGGING_RAISE)


def test_burn_insufficient_currency_balance(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    attacker = {"name": "leonidas", "key": "tz1ZrWi7V8tu3tVepAQVAEt8jgLz4VVEEf7m", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)

    transaction = market.burn(market_id, attacker['name'], 100)
    with pytest.raises(RpcError, match=r'Not enough balance in source account'):
        log_and_submit(
            transaction, attacker, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )

"""
Swap token
"""


# def check_that_swap_was_correct(before_supply, buy_token_name, sell_token_name, sell_quantity):
#     k = before_supply[buy_token_name]['total_supply'] * before_supply[sell_token_name]['total_supply']
#     token_sell_new_supply = before_supply[sell_token_name]['total_supply'] + sell_quantity
#     token_buy_new_supply = k / token_sell_new_supply
#     return token_sell_new_supply, token_buy_new_supply

@pytest.mark.parametrize('token_type', ["yes", "no"])
def test_swap_token_token_on_cleared(market, token_type, stablecoin_id):
    # quantity = 20000
    quantity = 200
    min_buy = 5
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error)
    transaction = market.mint(market_id, caller['name'], 3 * quantity)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error)
    transaction = market.swap_tokens(market_id, caller['name'], token_type, quantity, min_buy)
    before_storage, after_storage = log_and_submit(
        transaction,
        caller,
        market,
        market_id,
        error_func=raise_error
    )
    lst_token = ["yes", "no"]
    lst_token.remove(token_type)
    before_ledger_supply = before_storage["ledger_map"]
    after_ledger_supply = after_storage["ledger_map"]
    token_to_sell = token_type + '_token'
    token_to_buy = lst_token[0] + '_token'
    name = caller['name']
    assert after_ledger_supply[name][token_to_sell] == before_ledger_supply[name][token_to_sell] - quantity
    assert after_ledger_supply[name][token_to_buy] >= before_ledger_supply[name][token_to_buy]


def test_swap_token_token_in_auction_phase(market, stablecoin_id):
    quantity = 200
    min_buy = 5
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.swap_tokens(market_id, caller['name'], "yes", 100, 5)
    with pytest.raises(RpcError, match=r'Market not bootstrapped'):
        log_and_submit(
            transaction, caller, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_swap_token_resolved_market(market, stablecoin_id):
    quantity = 200
    min_buy = 5
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.mint(market_id, caller['name'], 3 * quantity)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error)
    transaction = market.close_market(market_id, caller['name'], True)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=True)
    transaction = market.swap_tokens(market_id, caller['name'], "yes", 100, 5)
    with pytest.raises(RpcError, match=r'Market has already been resolved'):
        log_and_submit(
            transaction, caller, market, market_id, error_func=raise_error,  logging=LOGGING_RAISE
        )


def test_swap_token_inexistent_market(market):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    transaction = market.swap_tokens(1, caller['name'], "yes", 100, 5)
    with pytest.raises(RpcError, match=r'No such market'):
        log_and_submit(
            transaction, caller, market, 1, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_swap_tokens_insufficient_currency_balance(market, stablecoin_id):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    attacker = {"name": "stavros", "key": "tz1iPFr4obPeSzknBPud8uWXZC7j5gKoah8d", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.swap_tokens(market_id, attacker['name'], "yes", 100, 5)
    with pytest.raises(RpcError, match=r'Not enough balance in source account'):
        log_and_submit(
            transaction, attacker, market, attacker, error_func=raise_error, logging=LOGGING_RAISE
        )

"""
Add liquidity
"""


def test_add_liquidity_on_cleared(market, stablecoin_id):
    quantity = 100
    end = datetime.now() + timedelta(minutes=0.02)
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error)
    transaction = market.mint(market_id, caller['name'], 2 * quantity)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error)
    transaction = market.auction_withdraw(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.update_liquidity(market_id, caller['name'], "payIn", quantity, quantity * 3, quantity * 3)
    before_storage, after_storage = log_and_submit(
        transaction,
        caller,
        market,
        market_id,
        error_func=raise_error,
        debug=True
    )
    before_ledger = before_storage["ledger_map"]
    after_ledger = after_storage["ledger_map"]
    name = caller['name']
    assert before_ledger[name]['pool_liquidity'] + quantity == after_ledger[name]['pool_liquidity']
    assert before_ledger[name]['yes_token'] != after_ledger[name]['yes_token']
    assert before_ledger[name]['no_token'] != after_ledger[name]['no_token']


def test_add_liquidity_in_auction_phase(market, stablecoin_id):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    quantity = 100
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.update_liquidity(market_id, caller['name'], "payIn", quantity, quantity * 3, quantity * 3)
    with pytest.raises(RpcError, match=r'Market not bootstrapped'):
        log_and_submit(
            transaction, caller, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )

def test_add_liquidity_non_withdraw(market, stablecoin_id):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    quantity = 100
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.update_liquidity(market_id, caller['name'], "payIn", quantity, quantity * 3, quantity * 3)
    with pytest.raises(RpcError, match=r'Withdraw auction bet before further liquidity'):
        log_and_submit(
            transaction, caller, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_add_liquidity_resolved_market(market, stablecoin_id):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.multiple_bids(market_id)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.close_market(market_id, caller['name'], True)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_withdraw(market_id, caller["name"])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.update_liquidity(market_id, caller['name'], "payIn", 300, 900, 900)
    with pytest.raises(RpcError, match=r'Market has already been resolved'):
        log_and_submit(
            transaction, caller, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_add_liquidity_inexistent_market(market):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    transaction = market.update_liquidity(1, caller['name'], "payIn", 300, 100, 100)
    with pytest.raises(RpcError, match=r'No such market'):
        log_and_submit(
            transaction, caller, 1, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_add_liquidity_insufficient_currency_balance(market, stablecoin_id):
    quantity = 100
    end = datetime.now() + timedelta(minutes=0.02)
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    attacker = {"name": "stavros", "key": "tz1iPFr4obPeSzknBPud8uWXZC7j5gKoah8d", "status": "created"}
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error)
    transaction = market.update_liquidity(market_id, attacker['name'], "payIn", 300, 900, 900)
    with pytest.raises(RpcError, match=r'Not enough balance in source account'):
        log_and_submit(
            transaction, attacker, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )

"""
Remove liquidity
"""


def test_remove_liquidity_on_cleared(market, stablecoin_id):
    quantity = 100
    end = datetime.now() + timedelta(minutes=0.02)
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error)
    transaction = market.mint(market_id, caller['name'], 4 * quantity)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error)
    transaction = market.auction_withdraw(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.update_liquidity(market_id, caller['name'], "payIn",  quantity, 3 * quantity, 3 * quantity)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.update_liquidity(market_id, caller['name'], "payOut", 2 * quantity, quantity, quantity)
    before_storage, after_storage = log_and_submit(
        transaction,
        caller,
        market,
        market_id,
        error_func=raise_error,
        debug=True
    )
    before_ledger = before_storage["ledger_map"]
    after_ledger = after_storage["ledger_map"]
    logger.error(before_ledger)
    logger.error(after_ledger)
    name = caller['name']
    assert before_ledger[name]['pool_liquidity'] - quantity * 2 == after_ledger[name]['pool_liquidity']
    assert before_ledger[name]['yes_token'] != after_ledger[name]['yes_token']
    assert before_ledger[name]['no_token'] != after_ledger[name]['no_token']


def test_remove_liquidity_in_auction_phase(market, stablecoin_id):
    quantity = 100
    end = datetime.now() + timedelta(minutes=0.02)
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.update_liquidity(market_id, caller['name'], "payOut", 100, 100, 100)
    with pytest.raises(RpcError, match=r'Market not bootstrapped'):
        log_and_submit(transaction, caller, market, market_id, error_func=raise_error)


def test_remove_liquidity_resolved_market(market, stablecoin_id):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.02)
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.multiple_bids(market_id)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.close_market(market_id, caller['name'], True)
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_withdraw(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.update_liquidity(market_id, caller['name'], "payOut", 100, 100, 100)
    with pytest.raises(RpcError, match=r'Market has already been resolved'):
        log_and_submit(
            transaction, caller, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_remove_liquidity_inexistent_market(market):
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    transaction = market.update_liquidity(1, caller['name'], "payOut", 100, 100, 100)
    with pytest.raises(RpcError, match=r'No such market'):
        log_and_submit(
            transaction, caller, market, 1, error_func=raise_error, logging=LOGGING_RAISE
        )


def test_remove_liquidity_insufficient_currency_balance(market, stablecoin_id):
    quantity = 100
    end = datetime.now() + timedelta(minutes=0.02)
    caller = {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"}
    attacker = {"name": "stavros", "key": "tz1iPFr4obPeSzknBPud8uWXZC7j5gKoah8d", "status": "created"}
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.auction_clear(market_id, caller['name'])
    log_and_submit(transaction, attacker, market, market_id, error_func=raise_error)
    transaction = market.auction_withdraw(market_id, caller['name'])
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)
    transaction = market.update_liquidity(market_id, attacker['name'], "payOut", 100, 100, 100)
    with pytest.raises(RpcError, match=r'Not enough balance in source account'):
        log_and_submit(
            transaction, attacker, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


"""
Resolve Market
"""


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_in_cleared_phase(market, token_type):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.close_market(market_id, account['name'], token_type)
    before_storage, after_storage = log_and_submit(transaction, account, market, market_id, logging=True)
    state = after_storage['market_map']['state']
    assert 'marketBootstrapped' in state
    assert 'auctionRunning' not in state
    assert state['marketBootstrapped']['resolution'] is not None


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_in_auction_phase(market, token_type):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)

    transaction = market.close_market(market_id, account['name'], token_type)
    before_storage, after_storage = log_and_submit(
        transaction,
        account,
        market,
        market_id,
        error_func=raise_error
    )
    state = after_storage['market_map']['state']
    assert 'marketBootstrapped' in state
    assert 'auctionRunning' not in state
    assert state['marketBootstrapped']['resolution'] is not None


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_already_resolved(market, token_type):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.close_market(market_id, account['name'], token_type)
    log_and_submit(transaction, account, market, market_id, logging=True)
    
    transaction = market.close_market(market_id, account['name'], token_type)
    with pytest.raises(RpcError, match=r'Market has already been resolved'):
        log_and_submit(
            transaction, account, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_unauthorized_account(market, token_type):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    attacker = {"name": "leonidas", "key": "tz1ZrWi7V8tu3tVepAQVAEt8jgLz4VVEEf7m", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    
    transaction = market.close_market(market_id, attacker['name'], token_type)
    with pytest.raises(RpcError, match=r'Access denied: unauthorized caller'):
        log_and_submit(
            transaction, attacker, market, market_id, error_func=raise_error, logging=LOGGING_RAISE
        )


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_non_existent_market_id(market, token_type):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    transaction = market.close_market(1, account['name'], token_type)
    with pytest.raises(RpcError, match=r'No such market'):
        log_and_submit(transaction, account, market, 1, error_func=raise_error, logging=LOGGING_RAISE)

''' 
Claim winnings
'''

@pytest.mark.parametrize('token_type', [True, False])
def test_claim_winning_lqt_provider(market, token_type):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.close_market(market_id, account['name'], token_type)
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_withdraw(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.claim_winnings(market_id, account['name'])
    before_storage, after_storage = log_and_submit(
        transaction,
        account,
        market,
        market_id,
        error_func=raise_error
    )

    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    end = datetime.now() + timedelta(minutes=0.002)

    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        account["name"],
        1000,
        2 ** 63,
        account['key'],
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=None #stablecoin_id
    )
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.auction_clear(market_id, account["name"])
    log_and_submit(transaction, account, market, market_id, logging=True)
    transaction = market.claim_winnings(market_id, account['name'])
    with pytest.raises(RpcError, match=r'Market not resolved'):
        log_and_submit(transaction, account, market, market_id, error_func=raise_error, logging=LOGGING_RAISE)


def test_claim_winnings_non_existent_market(market):
    account = {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"}
    transaction = market.claim_winnings(1, account['name'])
    with pytest.raises(RpcError, match=r'No such market'):
        log_and_submit(transaction, account, market, 1, error_func=raise_error, logging=LOGGING_RAISE)
