import random
from time import sleep
from datetime import datetime, timedelta
from os import stat_result

import pytest
from loguru import logger
from pytezos.rpc.node import RpcError

from tests.conftest import *
from tests.sandbox import SandboxedTestCase
from src.utils import get_tokens_id_list, log_and_submit, raise_error
from src.utils import id_generator

"""
Create Market
"""


def test_create_market_correct_bet_success_fa12(
        stablecoin_id,
        market,
        revealed_account
):
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        revealed_account["name"],
        quantity,
        2 ** 32,
        id_generator(15),
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
    storage = market.get_storage(market_id, revealed_account['name'])
    metadata = storage['market_map']['metadata']
    state = storage['market_map']['state']
    liquidity = storage['liquidity_provider_map']
    name = revealed_account['name']
    assert metadata['adjudicator'] == revealed_account['key']
    assert 'auctionRunning' in state
    assert state['auctionRunning']['quantity'] == quantity
    # yes_preference should be probability * quantity
    assert state['auctionRunning']['yes_preference'] == (2 ** 32 * quantity)
    assert state['auctionRunning']['uniswap_contribution'] == (2 ** 32 * quantity)
    assert liquidity[name]['bet']['quantity'] == quantity
    assert int(liquidity[name]['bet']['predicted_probability']) == int(2 ** 32)


# test_create_market_correct_bet_success_fa2

def test_create_market_non_existent_currency(market, revealed_account):
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        revealed_account['name'],
        quantity,
        2 ** 32,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract="KT1VKHPi2rWsRGPpZ6WpNxrKGtGA1LRcgFAp"
    )
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, market_id, error_func=raise_error)


@pytest.mark.parametrize("quantity,rate", [[0, 2 ** 34], [1000, 2 ** 65]])
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
        logger.info(f'{quantity} {rate}')
        log_and_submit(transaction, revealed_account, market, market_id, error_func=raise_error)


def test_create_market_already_used_market_id(stablecoin_id, market, revealed_account):
    quantity = 1000
    end = datetime.now() + timedelta(minutes=5)
    auction = get_random_market()
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        revealed_account['name'],
        quantity,
        2 ** 32,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=auction['id'],
        token_contract=stablecoin_id
    )
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], auction["id"], error_func=raise_error)


"""
Bet on Market 
"""


def test_auction_bet_new_address_correct_bet(market, revealed_account):
    auction = get_random_market(["created"])
    quantity = 1000
    rate = 2 ** 32
    transaction = market.bid_auction(auction['id'], revealed_account['name'], quantity, rate)
    log_and_submit(transaction, revealed_account, market, auction["id"], error_func=raise_error)
    storage = market.get_storage(auction['id'], revealed_account['name'])
    name = revealed_account['name']
    bet = storage['liquidity_provider_map'][name]['bet']
    assert bet['quantity'] == quantity
    assert bet['predicted_probability'] == rate


def test_auction_bet_existing_address_correct_bet(market, revealed_account):
    auction = get_random_market(["bidded"])
    quantity = 1000
    rate = 2 ** 32
    transaction = market.bid_auction(auction['id'], revealed_account["name"], quantity, rate)
    log_and_submit(transaction, revealed_account, market, auction["id"], error_func=raise_error)
    storage = market.get_storage(auction['id'], revealed_account['name'])
    name = revealed_account['name']
    bet = storage['liquidity_provider_map'][name]['bet']
    assert bet['quantity'] == quantity
    assert bet['predicted_probability'] == rate


@pytest.mark.parametrize("quantity,rate", [[0, 2 ** 34], [1000, 2 ** 65]])
def test_auction_incorrect_bet(market, revealed_account, quantity, rate):
    auction = get_random_market(["created"])
    transaction = market.bid_auction(auction['id'], revealed_account['name'], quantity, rate)
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, auction["id"], error_func=raise_error)


def test_auction_bet_insufficient_currency_balance(market, non_financed_account):
    auction = get_random_market(["bidded"])
    quantity = 1000
    rate = 2 ** 32
    transaction = market.bid_auction(auction['id'], non_financed_account["name"], quantity, rate)
    with pytest.raises(RpcError):
        log_and_submit(transaction, non_financed_account, auction["id"], error_func=raise_error)


def test_auction_bet_non_existent_market_id(market, revealed_account):
    transaction = market.bid_auction(1, revealed_account['name'], 1000, 2 * 32)
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, 1, error_func=raise_error)


def test_auction_bet_market_already_cleared(market, revealed_account):
    auction = get_random_market(["cleared"])
    transaction = market.bid_auction(auction['id'], revealed_account['name'], 1000, 2 * 32)
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, auction['id'], error_func=raise_error)


"""
Clear market
"""


def test_clear_market_in_auction_phase(market):
    auction = get_random_market(["bidded"])
    transaction = market.auction_clear(auction['id'], auction['caller']['name'])
    _before_storage, after_storage = log_and_submit(
        transaction,
        auction['caller'],
        market,
        auction["id"],
        error_func=raise_error
    )
    state = after_storage['market_map']['state']
    assert 'marketBootstrapped' in state
    assert 'auctionRunning' not in state
    assert state['marketBootstrapped']['resolution'] is None


def test_clear_market_with_no_bet_market(market):
    auction = get_random_market(["created"])
    transaction = market.auction_clear(auction['id'], auction['caller']['name'])
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction['id'], error_func=raise_error)


@pytest.mark.parametrize("quantity,rate", [[1, 100], [1, 2]])
def test_clear_market_insufficient_liquidity_from_bets(market, revealed_account, quantity, rate):
    auction = get_random_market(["created"])
    transaction = market.auction_clear(auction['id'], revealed_account['name'])
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, auction['id'], error_func=raise_error)


def test_clear_market_on_cleared(market):
    auction = get_random_market(["cleared"])
    transaction = market.auction_clear(auction['id'], auction['caller']['name'])
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction['id'], error_func=raise_error)


def test_clear_non_existent_market_id(market, revealed_account):
    transaction = market.auction_clear(1, revealed_account['name'])
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, 1, error_func=raise_error)


"""
Auction withdraw
"""


def test_withdraw_auction_cleared(market, revealed_account):
    end = datetime.now() + timedelta(minutes=5)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        revealed_account["name"],
        0,
        2 ** 32,
        "dededede",
        auction_end_date=end.timestamp(),
        market_id=None,
        token_contract=stablecoin_id
    )
    transaction = market.auction_withdraw(market_id, revealed_account['name'])
    # this should be working
    before_storage, after_storage = log_and_submit(
        transaction,
        revealed_account,
        market,
        market_id,
        error_func=raise_error
    )


def test_withdraw_auction_bidded(market, revealed_accounts, stablecoin_id):
    auction = get_random_market(["bidded"])
    quantity = random.randint(0, 900)
    rate = random.randint(0, 2 ** 63)
    end_delay = random.uniform(0.05, 0.10)
    end = datetime.now() + timedelta(minutes=end_delay)
    caller = random.choice(revealed_accounts)
    """
    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        quantity,
        rate,
        id_generator(),s
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market_id, error_func=raise_error)
    time.sleep(10)
    """
    transaction = market.auction_withdraw(auction['id'], auction['caller']['name'])
    storage = market.get_storage(auction['id'], auction['caller']['name'])
    state_of_market = storage['market_map']['state']
    logger.debug(f"state map = {state_of_market}")
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction['id'], error_func=raise_error)


def test_withdraw_auction_resolved(market):
    auction = get_random_market(["resolved"])
    transaction = market.auction_withdraw(auction['id'], auction['caller']['name'])
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction['id'], error_func=raise_error)


def test_withdraw_auction_non_existent_market_id(market, revealed_account):
    transaction = market.auction_withdraw(1, revealed_account['name'])
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, 1, error_func=raise_error)


"""
Mint token
"""


def test_mint_token_on_cleared(market, minter_account):
    quantity = 100
    auction = get_random_market(["minted"])
    transaction = market.mint(auction['id'], minter_account['name'], quantity)
    before_storage, after_storage = log_and_submit(
        transaction,
        minter_account,
        market,
        auction['id'],
        error_func=raise_error
    )
    before_supply = before_storage["supply_map"]
    after_supply = after_storage["supply_map"]
    assert before_supply['no_token']['total_supply'] + quantity == after_supply['no_token']['total_supply']
    assert before_supply['yes_token']['total_supply'] + quantity == after_supply['yes_token']['total_supply']


def test_mint_token_in_auction_phase(market, minter_account):
    auction = get_random_market(["bidded"])
    transaction = market.mint(auction['id'], minter_account['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_mint_resolved_market(market, minter_account):
    auction = get_random_market(["resolved"])
    transaction = market.mint(auction['id'], minter_account['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_mint_inexistent_market(market, minter_account):
    transaction = market.mint(1, minter_account['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, 1, error_func=raise_error)


def test_mint_insufficient_currency_balance(market, non_financed_account):
    auction = get_random_market(["cleared"])
    transaction = market.mint(auction['id'], non_financed_account['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, non_financed_account, market, auction["id"], error_func=raise_error)


"""
Burn token
"""


def test_burn_token_on_cleared(market, minter_account):
    quantity = 100
    auction = get_random_market(["minted"])
    transaction = market.burn(auction['id'], minter_account['name'], quantity)
    before_storage, after_storage = log_and_submit(
        transaction,
        minter_account,
        market,
        auction['id'],
        error_func=raise_error
    )
    before_supply = before_storage["supply_map"]
    after_supply = after_storage["supply_map"]
    assert before_supply['no_token']['total_supply'] - quantity == after_supply['no_token']['total_supply']
    assert before_supply['yes_token']['total_supply'] - quantity == after_supply['yes_token']['total_supply']


def test_burn_token_in_auction_phase(market, minter_account):
    auction = get_random_market(["bidded"])
    transaction = market.burn(auction['id'], minter_account['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_burn_resolved_market(market, minter_account):
    auction = get_random_market(["resolved"])
    transaction = market.burn(auction['id'], minter_account['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_burn_inexistent_market(market, minter_account):
    transaction = market.burn(1, minter_account['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, 1, error_func=raise_error)


def test_burn_insufficient_currency_balance(market, non_financed_account):
    auction = get_random_market(["cleared"])
    transaction = market.burn(auction['id'], non_financed_account['name'], 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, non_financed_account, market, auction["id"], error_func=raise_error)


"""
Swap token
"""


# def check_that_swap_was_correct(before_supply, buy_token_name, sell_token_name, sell_quantity):
#     k = before_supply[buy_token_name]['total_supply'] * before_supply[sell_token_name]['total_supply']
#     token_sell_new_supply = before_supply[sell_token_name]['total_supply'] + sell_quantity
#     token_buy_new_supply = k / token_sell_new_supply
#     return token_sell_new_supply, token_buy_new_supply

@pytest.mark.parametrize('token_type', ["yes", "no"])
def test_swap_token_token_on_cleared(market, minter_account, token_type):
    # quantity = 20000
    # auction = get_random_market(["minted"])
    quantity = 200
    min_buy = 30
    auction = get_random_market(["cleared"])
    transaction = market.mint(auction['id'], minter_account['name'], 2 * quantity)
    log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)
    transaction = market.swap_tokens(auction['id'], minter_account['name'], token_type, quantity, min_buy)
    before_storage, after_storage = log_and_submit(
        transaction,
        minter_account,
        market,
        auction['id'],
        error_func=raise_error
    )
    lst_token = ["yes", "no"]
    lst_token.remove(token_type)
    before_ledger_supply = before_storage["ledger_map"]
    after_ledger_supply = after_storage["ledger_map"]
    token_to_sell = token_type + '_token'
    token_to_buy = lst_token[0] + '_token'
    assert after_ledger_supply[token_to_sell] == before_ledger_supply[token_to_sell] - quantity
    assert after_ledger_supply[token_to_buy] >= before_ledger_supply[token_to_buy]


def test_swap_token_token_in_auction_phase(market, minter_account):
    auction = get_random_market(["bidded"])
    transaction = market.swap_tokens(auction['id'], minter_account['name'], "yes", 100, 5)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_swap_token_resolved_market(market, minter_account):
    auction = get_random_market(["resolved"])
    transaction = market.swap_tokens(auction['id'], minter_account['name'], "yes", 100, 5)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_swap_token_inexistent_market(market, minter_account):
    auction = get_random_market(["minted"])
    transaction = market.swap_tokens(1, minter_account['name'], "yes", 100, 5)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, 1, error_func=raise_error)


def test_swap_tokens_insufficient_currency_balance(market, non_financed_account):
    auction = get_random_market(["minted"])
    transaction = market.swap_tokens(auction['id'], non_financed_account['name'], "yes", 100, 5)
    with pytest.raises(RpcError):
        log_and_submit(transaction, non_financed_account, market, auction["id"], error_func=raise_error)


"""
Add liquidity
"""


def test_add_liquidity_on_cleared(market, minter_account):
    quantity = 100
    auction = get_random_market(["minted"])
    transaction = market.update_liquidity(auction['id'], minter_account['name'], "payIn", quantity)
    log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)
    before_storage, after_storage = log_and_submit(
        transaction,
        minter_account,
        market,
        auction['id'],
        error_func=raise_error
    )
    before_ledger = before_storage["ledger_map"]
    after_ledger = after_storage["ledger_map"]
    name = minter_account['name']
    logger.error(before_ledger)
    logger.error(after_ledger)
    logger.error(before_ledger[name])
    logger.error(after_ledger[name])
    assert before_ledger[name]['pool_liquidity'] + quantity == after_ledger['pool_liquidity']
    assert before_ledger[name]['yes_token'] != after_ledger['yes_token']
    assert before_ledger[name]['no_token'] != after_ledger['no_token']


def test_add_liquidity_in_auction_phase(market, minter_account):
    auction = get_random_market(["bidded"])
    transaction = market.update_liquidity(auction['id'], minter_account['name'], "payIn", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_add_liquidity_resolved_market(market, minter_account):
    auction = get_random_market(["resolved"])
    transaction = market.update_liquidity(auction['id'], minter_account['name'], "payIn", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_add_liquidity_inexistent_market(market, minter_account):
    transaction = market.update_liquidity(1, minter_account['name'], "payIn", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, 1, error_func=raise_error)


def test_add_liquidity_insufficient_currency_balance(market, non_financed_account):
    auction = get_random_market(["minted"])
    transaction = market.update_liquidity(auction['id'], non_financed_account['name'], "payIn", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, non_financed_account, market, auction["id"], error_func=raise_error)


"""
Remove liquidity
"""


def test_remove_liquidity_on_cleared(market, minter_account):
    quantity = 100
    auction = get_random_market(["minted"])
    transaction = market.update_liquidity(auction['id'], minter_account['name'], "payIn", quantity)
    log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)
    transaction = market.update_liquidity(auction['id'], minter_account['name'], "payOut", quantity)
    before_storage, after_storage = log_and_submit(
        transaction,
        minter_account,
        market,
        auction['id'],
        error_func=raise_error
    )
    before_ledger = before_storage["ledger_map"]
    after_ledger = after_storage["ledger_map"]
    logger.error(after_ledger)
    logger.error(before_ledger)
    # check with dani
    name = minter_account['name']
    assert before_ledger[name]['pool_liquidity'] - quantity == after_ledger['pool_liquidity']
    assert before_ledger[name]['yes_token'] != after_ledger['yes_token']
    assert before_ledger[name]['no_token'] != after_ledger['no_token']


def test_remove_liquidity_in_auction_phase(market, minter_account):
    auction = get_random_market(["bidded"])
    transaction = market.update_liquidity(auction['id'], minter_account['name'], "payOut", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_remove_liquidity_resolved_market(market, minter_account):
    auction = get_random_market(["resolved"])
    transaction = market.update_liquidity(auction['id'], minter_account['name'], "payOut", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_remove_liquidity_inexistent_market(market, minter_account):
    transaction = market.update_liquidity(1, minter_account['name'], "payOut", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, 1, error_func=raise_error)


def test_remove_liquidity_insufficient_currency_balance(market, non_financed_account):
    auction = get_random_market(["minted"])
    transaction = market.update_liquidity(auction['id'], non_financed_account['name'], "payIn", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, non_financed_account, market, auction["id"], error_func=raise_error)


"""
Resolve Market
"""


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_in_cleared_phase(market, revealed_account, token_type):
    auction = get_random_market(["cleared"])
    transaction = market.close_market(auction['id'], auction['caller']['name'], token_type)
    log_and_submit(transaction, auction['caller'], market, auction['id'], error_func=raise_error)
    storage = market.get_storage(auction['id'], auction['caller']['name'])
    state = storage['market_map']['state']
    assert 'marketBootstrapped' in state
    assert 'auctionRunning' not in state
    assert state['marketBootstrapped']['resolution'] is not None


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_in_auction_phase(market, token_type):
    auction = get_random_market(["bidded"])
    transaction = market.close_market(auction['id'], auction['caller']['name'], token_type)
    before_storage, after_storage = log_and_submit(
        transaction,
        auction['caller'],
        market,
        auction['id'],
        error_func=raise_error
    )
    state = after_storage['market_map']['state']
    assert 'marketBootstrapped' in state
    assert 'auctionRunning' not in state
    assert state['marketBootstrapped']['resolution'] is not None


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_already_resolved(market, token_type):
    auction = get_random_market(["resolved"])
    transaction = market.close_market(auction['id'], auction['caller']['name'], token_type)
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, auction["id"], error_func=raise_error)


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_market_unauthorized_account(market, revealed_account, token_type):
    auction = get_random_market(["cleared"])
    transaction = market.close_market(auction['id'], revealed_account['name'], token_type)
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, auction["id"], error_func=raise_error)


@pytest.mark.parametrize('token_type', [True, False])
def test_resolve_non_existent_market_id(market, revealed_account, token_type):
    transaction = market.close_market(1, revealed_account['name'], token_type)
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, 1, error_func=raise_error)


@pytest.mark.parametrize('token_type', [True, False])
def test_claim_winning_lqt_provider(market, minter_account, token_type):
    auction = get_random_market('minted')
    transaction = market.close_market(auction['id'], auction['caller']['name'], token_type)
    log_and_submit(transaction, auction['caller'], market, auction['id'], error_func=raise_error)
    transaction = market.claim_winnings(auction['id'], auction['caller']['name'])
    before_storage, after_storage = log_and_submit(
        transaction,
        auction['caller'],
        market=market,
        market_id=auction['id'],
        error_func=raise_error
    )


def test_claim_winnings_unresolved_market(market):
    auction = get_random_market('cleared')
    transaction = market.claim_winnings(auction['id'], auction['caller']['name'])
    with pytest.raises(RpcError):
        log_and_submit(transaction, auction['caller'], market, 1, error_func=raise_error)

    def test_claim_winnings_non_existent_market(market, minter_account):
        transaction = market.claim_winnings(1, minter_account['name'])
        with pytest.raises(RpcError):
            log_and_submit(transaction, minter_account, market, 1, error_func=raise_error)
