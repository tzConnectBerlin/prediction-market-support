#!/usr/bin/env python
"""
Tooling for prediction markets market
"""

import random
from typing import List, Optional

import typer
import ipfshttpclient

from src.accounts import Accounts
from src.config import Config
from src.market import Market
from src.stablecoin import Stablecoin
from src.utils import get_stablecoin, get_public_key

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
        quantity: int = typer.Argument(5000 * MULTIPLIER),
        rate: int = typer.Argument(random.randint(1, 99) * MULTIPLIER),
        auction_end_date: float = typer.Argument(30),
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
    market_id = state["market"].ask_question(
        question,
        answer,
        user,
        quantity,
        rate,
        auction_end_date
    )
    print(f"Created market {market_id} in PM contract")
    return market_id


@app.command()
def bid_auction(
        market_id: int,
        user: str,
        quantity: int = typer.Argument(500 * MULTIPLIER),
        rate: int = typer.Argument(random.randint(1, 99) * MULTIPLIER)
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
    state["market"].bid_auction(market_id, user, quantity, rate)


@app.command()
def random_bids(
        market_id: int,
        quantity: int = typer.Argument(500 * MULTIPLIER),
        rate: int = typer.Argument(random.randint(1, 99) * MULTIPLIER),
):
    """
    Launch random bid on a auction for all of the chosen users folder

    market_id: Contract on which the bid are made
    """
    if len(state["accounts"].names()) == 0:
        print("Please add some accounts before using this functionality")
    print("placing random bids")
    user_list = state["accounts"].names()
    with typer.progressbar(user_list) as progress:
        for user in progress:
            print(f"generating bids for accounts {user}")
            state["market"].bid_auction(
                market_id,
                user,
                quantity,
                rate
            )
        print("\n")


@app.command()
def clear_auction(market_id: int, user: str):
    """
    Clear the auction

    market_id: the id of the question
    """
    print(f"Clear an auction {market_id} for {user}")
    state["market"].auction_clear(market_id, user)


@app.command()
def withdraw_auction(market_id: int, user: str):
    """
    Withdraw the auction

    market_id: the id of the question
    """
    print(f"Withdraw an auction {market_id} for {user}")
    state["market"].auction_withdraw(market_id, user)


@app.command()
def enter_market(
        market_id: int,
        user: str,
        amount: int
):
    state["market"].marketEnterExit(
        user,
        'PayIn',
        market_id,
        amount
    )


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
    state["market"].close_market(
        market_id,
        token_type,
        user
    )


@app.command()
def approve_market(
        user: str,
        amount: int
):
    """"
    Approve a quantity of stablecoin to be use by the market
    """
    check_account_loaded(user)
    state["stablecoin"].approve_market(user, amount)


@app.command()
def exit_market(
        market_id: int,
        user: str,
        amount: int
):
    state["market"].marketEnterExit(
        user,
        'PayOut',
        market_id,
        amount
    )


@app.command()
def swap_tokens(
        market_id: int,
        user: str,
        token_to_sell: str,
        amount: int
):
    state["market"].swapTokens(
        token_to_sell,
        market_id,
        amount,
        user
    )


def swap_liquidity(
        market_id: int,
        user: str,
        direction: str,
        amount: int
):
    state["market"].swapLiquidity(
        direction,
        market_id,
        amount,
        user
    )


@app.command()
def claim_winnings(
        market_id: int,
        user: str,
):
    """
    Claim winnings for user
    """
    check_account_loaded(user)
    state["market"].claim_winnings(
        market_id,
        user
    )


#@app.command()
def list_auctions():
    """
    List all current available questions
    """
    state["market"].list_markets()


#@app.command()
def list_bids(question: str):
    """
    List all the current bids on a question
    """
    state["market"].list_bids(question)


@app.command()
def mint(value: int, user: str):
    """
    Mint a quantity of stablecoin for user
    """
    check_account_loaded(user)
    state["market"].mint(user, value)


@app.command()
def burn(value: int, user: str):
    """
    Burn a quantity stablecoin for account
    """
    check_account_loaded(user)
    state["market"].burn(user, value)


@app.command()
def get_question_data(
        question: str
):
    ipfsclient = ipfshttpclient.connect(state['config']['ipfs_server'])
    data = ipfsclient.get_json(question)
    if data is not None:
        print(data)


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
    print("Transferring stablecoin to accounts:", state["accounts"].names())
    state["market"].fund_stablecoin(value)


@app.command()
def transfer_stablecoin(
        user: str,
        value: int = typer.Argument(100000 * MULTIPLIER)
):
    """
    Transfer a certain amount of coins toward an user address

    dest: user address that will receive the funds
    """
    check_account_loaded(user)
    print(f"Transferring stablecoin")
    state["market"].transfer_stablecoin_to_user(user, value)
    stablecoin_balance(user)


@app.command()
def stablecoin_balance(
        user: str
):
    """
    Get balance for user
    """
    check_account_loaded(user)
    user_address = get_public_key(state['accounts'][user])
    balance = int(get_stablecoin(state['config']['admin_account'],
                                 state['config']['contract']).getBalance(
        {'owner': user_address, 'contract_1': None}).view())
    balance /= MULTIPLIER
    print("balances:")
    print(f"{user}: {balance}")



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
    #test ignored accounts
    #test they are in accounts
    state['accounts'].import_from_tezos_client(ignored_accounts)
    state['market'] = Market(state['accounts'], state['config'])
    #state['stablecoin'] = Stablecoin(state['accounts'], state['config'])
    return state


if __name__ == "__main__":
    app()
