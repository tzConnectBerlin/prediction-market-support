#!/usr/bin/env python
"""
Tooling for prediction markets market
"""

import random
from typing import List, Optional

import typer

from src.accounts import Accounts
from src.config import Config
from src.market import Market

PERCENT = 10000000000000000

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
    management of accounts in the user folder
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
def list_accounts():
    """
    list all of the accounts
    """
    accounts = state['accounts']
    account_list = accounts.names()
    for account_name in account_list:
        print(
            f'name: {account_name}   balance: {accounts[account_name].balance()}'
        )


@app.command()
def ask_question(
        question: str,
        answer: str,
        user: str,
        quantity: int = typer.Argument(50000),
        rate: int = typer.Argument(random.randint(1, 99) * PERCENT),
        auction_end_date: float = typer.Argument(30),
        market_end_date: float = typer.Argument(50)
        ):
    """
    create a question in IPFS

    question: string representing the answer asked
    answer: string representing the possible answer
    user: string representing the questions owner
    quantity: integer representing the quantity of stable coin generated
    rate: rate
    """
    check_account_loaded(user)
    ipfs_hash = state["market"].ask_question(
                question,
                answer,
                user,
                quantity,
                rate,
                auction_end_date,
                market_end_date
            )
    print(f"Created market {ipfs_hash} in PM contract")
    return ipfs_hash


@app.command()
def fund_stablecoin(
        value: int = typer.Argument(1000000000)
        ):
    """
    fund all accounts with a random quantity of tezos

    value: the amont of tezos funded
    """
    print("Transferring stablecoin to accounts:", state["accounts"].names())
    state["market"].fund_stablecoin(value)


@app.command()
def transfer_stablecoin(
        user: str,
        value: int = typer.Argument(1000000000)
        ):
    """
    transfer a certain amount of coins toward an user address

    dest: user address that will receive the funds
    """
    check_account_loaded(user)
    print(f"Transferring stablecoin")
    state["market"].transfer_stablecoin_to_user(user, value)


@app.command()
def bid_auction(
        ipfs_hash: str,
        user: str,
        quantity: int = typer.Argument(50000),
        rate: int = typer.Argument(random.randint(1, 99) * PERCENT)
        ):
    """
    launch a bid on an auction

    ipfs_hash: the contract concerned by the bid
    user: string representing the user which is bidding during the auction
    quantity: Integer representing quantity of stable coins bid during the auction
    rate: What is rate?
    """
    check_account_loaded(user)
    print(f"bidding auction for {user}")
    state["market"].bid_auction(ipfs_hash, user, quantity, rate)


@app.command()
def random_bids(
        ipfs_hash: str,
        quantity: int = typer.Argument(50000),
        rate: int = typer.Argument(random.randint(1, 99) * PERCENT),
        ):
    """
    launch random bid on a auction for
    all of the chosen users folder

    ipfs_hash: Contract on which the bid are made
    """
    if len(state["accounts"].names()) == 0:
        print("Please add some accounts before using this functionality")
    print("placing random bids")
    user_list = state["acounts"].names()
    with typer.progressbar(user_list) as progress:
        for user in progress:
            print(f"generating bids for accounts {user}")
            state["market"].bid_auction(
                ipfs_hash,
                user,
                quantity,
                rate
            )
        print("\n")


@app.command()
def close_auction(ipfs_hash: str, user: str):
    """
    close the auction

    ipfs_hash: the hash of the concerned contract
    """
    print(f"closing action {ipfs_hash} for {user}")
    state["market"].close_auction(ipfs_hash, user)


@app.command()
def close_market(
        ipfs_hash: str,
        user: str,
        token_type: bool = typer.Argument(True)
        ):
    """
    close the market

    ipfs_hash: the hash of the concerned market
    token_type: type of the token
    user: owner of the market
    """
    check_account_loaded(user)
    print(f"closing market {ipfs_hash}")
    state["market"].close_market(
            ipfs_hash,
            token_type,
            user
    )


@app.callback()
def main(
        import_accounts: Optional[List[str]] = typer.Option(None, "--with-account", "-w"),
        ignored_accounts: Optional[List[str]] = typer.Option(None, "--ignore-account"),
        endpoint: str = typer.Option(None, "--endpoint", "-e"),
        contract: str = typer.Option(None, "--contract", "-c"),
        admin_key: str = typer.Option(None),
        config_file: str = typer.Option("oracle.ini"),
        force: bool = typer.Option(None, "--force", "-f")
        ):
    """
    High level option for the tool
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
    return state


if __name__ == "__main__":
    app()
