from datetime import datetime, timedelta
import time

import pytest
from pytezos.rpc.node import RpcError
from loguru import logger

from src.utils import get_tokens_id_list, log_and_submit, raise_error
from .conftest import get_random_market
import random
from src.utils import id_generator

"""
Create Market
"""


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
    storage = market.get_storage(market_id, revealed_account['name'])
    metadata = storage['market_map']['metadata']
    state = storage['market_map']['state']
    liquidity = storage['liquidity_provider_map']
    assert metadata['adjudicator'] == revealed_account['key']
    assert 'auctionRunning' in state
    assert state['auctionRunning']['quantity'] == quantity
    # yes_preference should be probability * quantity
    assert state['auctionRunning']['yes_preference'] == (2**32 * quantity)
    assert state['auctionRunning']['uniswap_contribution'] == (2**32 * quantity)
    assert liquidity['bet']['quantity'] == quantity
    assert int(liquidity['bet']['predicted_probability']) == int(2**32)

#test_create_market_correct_bet_success_fa2


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


@pytest.mark.parametrize("quantity,rate", [[0, 2**34], [1000, 2**65]])
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
        2**32,
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
    rate = 2**32
    transaction = market.bid_auction(auction['id'], revealed_account['name'], quantity, rate)
    log_and_submit(transaction, revealed_account, auction["id"], error_func=raise_error)
    storage = market.get_storage(auction['id'], revealed_account['name'])
    bet = storage['liquidity_provider_map']['bet']
    assert bet['quantity'] == quantity
    assert bet['predicted_probability'] == rate


def test_auction_bet_existing_address_correct_bet(market, revealed_account):
    auction = get_random_market(["bidded"])
    quantity = 1000
    rate = 2**32
    transaction = market.bid_auction(auction['id'], revealed_account["name"], quantity, rate)
    log_and_submit(transaction, revealed_account, auction["id"], error_func=raise_error)
    storage = market.get_storage(auction['id'], revealed_account['name'])
    bet = storage['liquidity_provider_map']["bet"]
    assert bet['quantity'] == quantity
    assert bet['predicted_probability'] == rate


@pytest.mark.parametrize("quantity,rate", [[0, 2**34], [1000, 2**65]])
def test_auction_incorrect_bet(market, revealed_account, quantity, rate):
    auction = get_random_market(["created"])
    transaction = market.bid_auction(auction['id'], revealed_account['name'], quantity, rate)
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, auction["id"], error_func=raise_error)


def test_auction_bet_insufficient_currency_balance(market, non_financed_account):
    auction = get_random_market(["bidded"])
    quantity = 1000
    rate = 2**32
    transaction = market.bid_auction(auction['id'], non_financed_account["name"], quantity, rate)
    log_and_submit(transaction, non_financed_account, auction["id"], error_func=raise_error)
    storage = market.get_storage(auction['id'], non_financed_account['name'])
    bet = storage['liquidity_provider_map']["bet"]
    assert bet['quantity'] == quantity
    assert bet['predicted_probability'] == rate


def test_auction_bet_non_existent_market_id(market, revealed_account):
    transaction = market.bid_auction(1, revealed_account['name'], 1000, 2*32)
    with pytest.raises(RpcError):
        log_and_submit(transaction, revealed_account, market, 1, error_func=raise_error)


def test_auction_bet_market_already_cleared(market, revealed_account):
    auction = get_random_market(["cleared"])
    transaction = market.bid_auction(auction['id'], revealed_account['name'], 1000, 2*32)
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


@pytest.mark.parametrize("quantity,rate", [[1, 100], [0, 2]])
def test_clear_market_insufficient_liquidity_from_bets(market, revealed_account, quantity, rate):
    auction = get_random_market(["created"])
    transaction = market.bid_auction(auction['id'], revealed_account['name'], quantity, rate)
    log_and_submit(transaction, revealed_account, market, auction['id'], error_func=raise_error)
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


def test_withdraw_auction_cleared(market):
    auction = get_random_market(["cleared"])
    transaction = market.auction_withdraw(auction['id'], auction['caller']['name'])
    before_storage, after_storage = log_and_submit(
        transaction,
        auction['caller'],
        market,
        auction["id"],
        error_func=raise_error
    )

import time

@pytest.mark.parametrize('random_nonce', [1,2,3,4,5,6,7,8])
def test_withdraw_auction_bidded(market, random_nonce, revealed_accounts, stablecoin_id):
    auction = get_random_market(["bidded"])
    quantity = random.randint(0, 900)
    rate = random.randint(0, 2 ** 63)
    end_delay = random.uniform(0.05, 0.15)
    end = datetime.now() + timedelta(minutes=end_delay)
    caller = random.choice(revealed_accounts)
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
    log_and_submit(transaction, caller, auction["id"], error_func=raise_error)
    time.sleep(10)
    transaction = market.auction_withdraw(market_id, caller['name'])
    with pytest.raises(RpcError):
        log_and_submit(transaction, caller, market, auction['id'], error_func=raise_error)


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
    tokens = get_tokens_id_list(auction['id'])
    assert after_supply != {}
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
    assert after_supply != {}
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
    quantity = 20000
    auction = get_random_market(["minted"])
    quantity = 200
    auction = get_random_market(["cleared"])
    transaction = market.mint(auction['id'], minter_account['name'], 2 * quantity)
    log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)
    transaction = market.swap_tokens(auction['id'], minter_account['name'], token_type, quantity)
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
    # token_sell_new_supply, token_buy_new_supply = check_that_swap_was_correct(before_supply, token_to_sell, token_to_buy, quantity)
    logger.debug(before_storage)
    logger.debug(after_storage)
    assert after_ledger_supply != {}
    assert after_ledger_supply[token_to_sell] == before_ledger_supply[token_to_sell] - quantity
    # logger.debug("############################################################################")
    # logger.debug("############################################################################")
    # logger.debug("############################################################################")
    # logger.debug(f"token to sell = {token_to_sell} and token to buy = {token_to_buy}")
    # logger.debug(f"before_supply dic.keys is = {before_supply.keys()}")
    # logger.debug(f"before_supply dic is = {before_supply}")
    # logger.debug(f"supply of token sell before = {before_supply[token_to_sell]}")
    # # logger.debug(f"token to sell new quantity by me = {token_sell_new_supply}")
    # logger.debug(f"token to sell new quantity by dani = {after_supply[token_to_sell]}")
    # logger.debug(f"supply of token buy before = {before_supply[token_to_buy]}")
    # # logger.debug(f"token to buy new quantity by me = {token_buy_new_supply}")
    # logger.debug(f"token to buy new quantity by dani = {after_supply[token_to_buy]}")
    
    # assert before_supply['no_token']['total_supply'] == after_supply['no_token']['total_supply']
    # assert before_supply['yes_token']['total_supply'] == after_supply['yes_token']['total_supply']
    # assert before_supply['pool_liquidity']['total_supply'] == after_supply['pool_liquidity']['total_supply']
    # assert before_supply['auction_reward']['total_supply'] == after_supply['auction_reward']['total_supply']



def test_swap_token_token_in_auction_phase(market, minter_account):
    auction = get_random_market(["bidded"])
    transaction = market.swap_tokens(auction['id'], minter_account['name'], "yes", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_swap_token_resolved_market(market, minter_account):
    auction = get_random_market(["resolved"])
    transaction = market.swap_tokens(auction['id'], minter_account['name'], "yes", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)


def test_swap_token_inexistent_market(market, minter_account):
    auction = get_random_market(["minted"])
    transaction = market.swap_tokens(1, minter_account['name'], "yes", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, minter_account, market, 1, error_func=raise_error)


def test_swap_tokens_insufficient_currency_balance(market, non_financed_account):
    auction = get_random_market(["minted"])
    transaction = market.swap_tokens(auction['id'], non_financed_account['name'], "yes", 100)
    with pytest.raises(RpcError):
        log_and_submit(transaction, non_financed_account, market, auction["id"], error_func=raise_error)


"""
Add liquidity
"""

#swap_liquidity should be renamed to update_liquidity
def test_add_liquidity_on_cleared(market, minter_account):
    quantity = 100
    auction = get_random_market(["minted"])
    transaction = market.update_liquidity(auction['id'], minter_account['name'], "payIn", 100)
    log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)
    before_storage, after_storage = log_and_submit(transaction, minter_account, market, 1, error_func=raise_error)
    after_ledger = after_storage["ledger_map"]
    logger.info(before_storage)
    logger.info(after_ledger)


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
    transaction = market.update_liquidity(auction['id'], minter_account['name'], "payOut", 100)
    log_and_submit(transaction, minter_account, market, auction["id"], error_func=raise_error)
    before_storage, after_storage = log_and_submit(
        transaction,
        minter_account,
        market,
        auction['id'],
        error_func=raise_error
    )
    assert False


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

#There is something wrong here to check, the market keep being shown as not existing
@pytest.mark.parametrize('token_type', [True, False])
def test_claim_winning_lqt_provider(market, minter_account, token_type):
    auction = get_random_market('minted')
    transaction = market.close_market(auction['id'], minter_account['name'], token_type)
    log_and_submit(transaction, auction['caller'], market, auction['id'], error_func=raise_error)
    time.sleep(10)
    transaction = market.claim_winnings(auction['id'], minter_account['name'])
    before_storage, after_storage = log_and_submit(
        transaction,
        minter_account,
        market,
        auction['id'],
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

<<<<<<< HEAD

=======
>>>>>>> e83ef5680881a86587b287bdc96d12b28be0e3ba
