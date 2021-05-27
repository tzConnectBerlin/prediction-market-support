#!/usr/bin/env python
"""
Tooling for prediction markets market
"""

import json
import random
from typing import List, Optional, Tuple, Union

import pytz
import typer
import ipfshttpclient
from datetime import datetime, timedelta
import dateparser

from src.accounts import Accounts
from src.config import Config
from src.market import Market
from src.stablecoin import Stablecoin
from src.utils import *

MULTIPLIER = 10 ** 6
##################
# Setup
##################

app = typer.Typer()

state = {
}


def check_account_loaded(account):
    if account not in state["accounts"]:
        print(f"account {account} not found, here are available accounts:")
        print(state["accounts"].names())
        raise typer.Exit()


@app.command()
def manage_accounts(
        activate: bool = typer.Option(False, "--activate", "-a"),
        reveal: bool = typer.Option(False, "--reveal", "-r"),
        import_accounts: bool = typer.Option(False, "--import", "-i"),
):
    """
    Management of accounts in the user folder
    """
    account_list = state["accounts"].names()
    with typer.progressbar(account_list) as progress:
        for user in progress:
            if import_accounts:
                if user is None:
                    print('please add user')
                    continue
                state['accounts'].import_to_tezos_client(user)
            if activate:
                state['accounts'].activate_account(user)
            if reveal:
                state['accounts'].reveal_account(user)


@app.command()
def ask_question(
        question: str,
        answer: str,
        user: str,
        ipfs_hash: str = typer.Argument(None),
        quantity: int = typer.Argument(5000 * MULTIPLIER),
        rate: int = typer.Argument(random.randint(0, 2 ** 64)),
        auction_end_date: str = typer.Argument("in 5 minutes")
):
    """
    Create a question in IPFS

    question: string representing the answer asked
    answer: string representing the possible answer
    user: string representing the questions owner
    quantity: integer representing the quantity of stable coin generated
    rate: rate
    """
    check_account_loaded(user)
    param = {
        'auctionEndDate': auction_end_date,
        'iconURL':
            'https://images-na.ssl-images-amazon.com/images/I/41GqyirrgbL._AC_SX425_.jpg',
        'question': question,
        'yesAnswer': answer,
    }
    try:
        auction_end_date = dateparser.parse(auction_end_date).timestamp()
    except:
        print("something is wrong with the chosen date format")
        exit()
    print(auction_end_date)
    if ipfs_hash is None:
        ipfs = ipfshttpclient.connect(state['config']['ipfs_server'])
        ipfs_hash = ipfs.add_str(json.dumps(param))
    market_id, transaction = state["market"].ask_question(
        question,
        answer,
        user,
        quantity,
        rate,
        ipfs_hash,
        auction_end_date
    )
    print(f"Created market {market_id} in PM contract")
    print(f'with variables: quandity : {quantity} + rate {rate}')
    #print(transaction.json_payload())
    submit_transaction(transaction, error_func=print_error)
    return market_id


@app.command()
def bid_auction(
        market_id: int,
        user: str,
        quantity: int = typer.Argument(500 * MULTIPLIER),
        rate: int = typer.Argument(random.randint(0, 2 ** 64))
):
    """
    Bid on an auction

    market_id: the contract to use
    user: string representing the user who is bidding
    quantity: quantity of stable coins bid during the auction
    rate: What is rate?
    """
    check_account_loaded(user)
    print(f"bidding auction for {user}")
    transaction = state["market"].bid_auction(market_id, user, quantity, rate)
    submit_transaction(transaction, error_func=print_error)


@app.command()
def random_bids(
        market_id: int,
        quantity: int = typer.Argument(500 * MULTIPLIER),
        rate: int = -1,
):
    """
    Launch random bid on a auction for all of the chosen users folder

    market_id: Contract on which the bid are made
    """
    if len(state["accounts"].names()) == 0:
        print("Please add some accounts before using this functionality")
    print("placing random bids")
    user_list = state["accounts"].names()
    transactions = []
    with typer.progressbar(user_list) as progress:
        for user in progress:
            actual_rate = rate if rate != -1 else random.randint(0, 2 ** 63)
            print(f"generating bids for accounts {user}")
            transaction = state["market"].bid_auction(
                market_id,
                user,
                quantity,
                actual_rate
            )
            transactions.append(transaction)
        bulk_transactions = state["config"]["admin_account"].bulk(*transactions)
        submit_transaction(bulk_transactions, error_func=print_error)
        print("\n")


@app.command()
def clear_market(market_id: int, user: str):
    """
    Clear the auction

    market_id: the id of the question
    """
    print(f"Clearing market {market_id} for {user}")
    transaction = state["market"].auction_clear(market_id, user)
    submit_transaction(transaction, error_func=print_error)


@app.command()
def withdraw_auction(market_id: int, user: str):
    """
    Withdraw the auction

    market_id: the id of the question
    """
    print(f"Withdraw an auction {market_id} for {user}")
    transaction = state["market"].auction_withdraw(market_id, user)
    submit_transaction(transaction, error_func=print_error)


@app.command()
def enter_market(
        market_id: int,
        user: str,
        amount: int
):
    """
    Enter the market
    """
    transaction = state["market"].market_enter_exit(
        market_id,
        user,
        'payIn',
        amount
    )
    submit_transaction(transaction, error_func=print_error)


@app.command()
def close_market(
        market_id: int,
        user: str,
        token_type: bool = typer.Argument(True)
):
    """
    Close the market

    market_id: the id of the concerned market
    token_type: type of the token
    user: owner of the market
    """
    check_account_loaded(user)
    print(f"closing market {market_id}")
    transaction = state["market"].close_market(
        market_id,
        user,
        token_type
    )
    submit_transaction(transaction, error_func=print_error)


@app.command()
def approve_market(
        user: str,
        amount: int
):
    """
    Approve a quantity of stablecoin to be use by the market
    """
    check_account_loaded(user)
    transaction = state["stablecoin"].approve_market(user, amount)
    submit_transaction(transaction, error_func=print_error)


@app.command()
def exit_market(
        market_id: int,
        user: str,
        amount: int
):
    """
    Exit the market
    """
    transaction = state["market"].marketEnterExit(
        market_id,
        user,
        'payOut',
        amount
    )
    submit_transaction(transaction, error_func=print_error)


@app.command()
def swap_tokens(
        market_id: int,
        user: str,
        token_to_sell: str,
        amount: int
):
    """
    Swap one outcome token through the liquidity pool for its opposing pair
    as a fixed input swap operation

    """
    transaction = state["market"].swap_tokens(
        market_id,
        user,
        token_to_sell,
        amount
    )
    submit_transaction(transaction, error_func=print_error)


@app.command()
def swap_liquidity(
        market_id: int,
        user: str,
        direction: str,
        amount: int
):
    """
    Update the liquidity for the market
    """
    transaction = state["market"].update_liquidity(
        market_id,
        user,
        direction,
        amount
    )
    submit_transaction(transaction, error_func=print_error)


@app.command()
def claim_winnings(
        market_id: int,
        user: str,
):
    """
    Claim winnings for user
    """
    check_account_loaded(user)
    transaction = state["market"].claim_winnings(
        market_id,
        user
    )
    submit_transaction(transaction, error_func=print_error)


@app.command()
def mint(
        market_id: int,
        user: str,
        amount: int
):
    """
    Mint a quantity of stablecoin for user
    """
    check_account_loaded(user)
    transaction = state["market"].mint(market_id, user, amount)
    submit_transaction(transaction, error_func=print_error)


@app.command()
def burn(
        market_id: int,
        user: str,
        amount: int
):
    """
    Burn a quantity stablecoin for account
    """
    check_account_loaded(user)
    transaction = state["market"].burn(market_id, user, amount)
    submit_transaction(transaction, error_func=print_error)


@app.command()
def get_market_metadata(
        market_id: int
):
    client = state['config']['admin_account']
    contract = state['config']['contract']
    data = get_market_map(client, contract, market_id)
    metadata = data['metadata']
    ipfsclient = ipfshttpclient.connect(state['config']['ipfs_server'])
    for k, v in metadata.items():
        print(k, v)
    if metadata['ipfs_hash'] is not None:
        print("ipfs data:")
        data = ipfsclient.get_json(metadata["ipfs_hash"])
        if data is not None:
            print(data)


@app.command()
def get_market_liquidity(
        market_id: int,
        user: str
):
    client = state['config']['admin_account']
    contract = state["config"]["contract"]
    address = get_public_key(state["accounts"][user])
    data = get_question_liquidity_provider_map(client, contract, market_id, address)
    for k, v in data.items():
        print(k, v)


@app.command()
def display_tokens(
        market_id: int,
        user: str
):
    client = state['config']['admin_account']
    contract = state['config']['contract']
    #address = get_public_key(state['accounts'][user])
    base_token_id = market_id << 3
    #ledger_map = get_tokens_ledgermap(client, contract)
    #ledger_map_key = {'owner': address, 'token_id': base_token_id}
    supply_map = get_tokens_supplymap(client, contract)
    #print(ledger_map[ledger_map_key]())
    print(supply_map[base_token_id]())


@app.command()
def list_accounts():
    """
    List all of the accounts
    """
    accounts = state['accounts']
    account_list = accounts.names()
    for account_name in account_list:
        print(
            f'name: {account_name}   balance: {accounts[account_name].balance()}'
        )


@app.command()
def fund_stablecoin(
        value: int = typer.Argument(100000 * MULTIPLIER)
):
    """
    Fund all accounts with a random quantity of tezos

    value: the amont of tezos funded
    """
    if len(state["accounts"].names()) == 0:
        print("Please add some accounts before using this functionality")
    user_list = state["accounts"].names()
    print("Transferring stablecoin to accounts:", state["accounts"].names())
    transactions = []
    with typer.progressbar(user_list) as progress:
        for user in progress:
            transaction = state["stablecoin"].fund(user, value)
            transactions.append(transaction)
        bulk_transactions = state["config"]["admin_account"].bulk(*transactions)
        submit_transaction(bulk_transactions, error_func=print_error)


@app.command()
def transfer_stablecoin(
        src: str,
        dest: str,
        value: int = typer.Argument(100000 * MULTIPLIER)
):
    """
    Transfer a certain amount of coins toward an user address

    dest: user address that will receive the funds
    """
    check_account_loaded(dest)
    check_account_loaded(src)
    print(f"Transferring stablecoin")
    transaction = state["stablecoin"].transfer(src, dest, value)
    submit_transaction(transaction, error_func=print_error)
    stablecoin_balance(src)
    stablecoin_balance(dest)


@app.command()
def stablecoin_balance(
        user: str
):
    """
    Get balance for user
    """
    check_account_loaded(user)
    balance = state["stablecoin"].get_balance(user)
    print(f"balance: {balance}")


@app.callback()
def main(
        import_accounts: Optional[List[str]] = typer.Option(None, "--with-account", "-w"),
        ignored_accounts: Optional[List[str]] = typer.Option(None, "--ignore-account"),
        endpoint: str = typer.Option(None, "--endpoint", "-e"),
        contract: str = typer.Option(None, "--contract", "-c"),
        admin_key: str = typer.Option(None),
        config_file: str = typer.Option("cli.ini"),
        force: bool = typer.Option(None, "--force", "-f")
):
    """
    High level options
    """
    state['config'] = Config(
        admin_account_key=admin_key,
        config_file=config_file,
        contract=contract,
        endpoint=endpoint,
    )
    state['accounts'] = Accounts(state['config']['endpoint'])
    if import_accounts is not None:
        for account in import_accounts:
            account_name = typer.prompt("Please associate a name for this account")
            state['accounts'].import_from_file(account, account_name)
            if force is not None:
                state["accounts"].import_to_tezos_client(account_name)
                typer.echo(f"{account_name} was imported")
                state["accounts"].activate_account(account_name)
                typer.echo(f"{account_name} was activated")
                state["accounts"].reveal_account(account_name)
                typer.echo(f"{account_name} was revealed")
    state['accounts'].import_from_tezos_client(ignored_accounts)
    state['market'] = Market(state['accounts'], state['config'])
    state['stablecoin'] = Stablecoin(state['accounts'], state['config'])
    return state

if __name__ == "__main__":
    app()
