#!python
"""
Tooling for prediction markets support
"""

import json
import random
import sys
from time import sleep
from typing import List, Optional

import configparser
import typer

##### Local Script
from src.accounts import Accounts
from src.utils import summary
from src.support import Support

PERCENT = 10000000000000000

##################
# Setup
##################

app = typer.Typer()

state = {
        "accounts": Accounts("http://localhost:20000", folder=None),
        "support": None
}

@app.command()
def manage_accounts(
        activate: bool = typer.Option(False, "--activate", "-a"),
        reveal: bool = typer.Option(False, "--reveal", "-r"),
        import_accounts: bool = typer.Option(False, "--import", "-i")
        ):
    """
    management of accounts in the user folder
    """
    with typer.progressbar(accounts.names()) as progress:
        for user in progress:
            if import_accounts:
                if user == None:
                    print("please add user")
                    return
                accounts.import_to_tezos_client(user)
            if activate:
                accounts.activate_account(user)
            if reveal:
                accounts.reveal_account(user)
            print("\n")
    support = Support(accounts, config_file="./oracle.ini")

@app.command()
def ask_question(
        question: str,
        answer: str,
        user: str,
        quantity: int = typer.Option(50000),
        rate: int = typer.Option(random.randint(1,99) * PERCENT),
        auction_end_date: int = typer.Option(30),
        market_end_date: int = typer.Option(50)
    ):
    """
    create a question in IPFS

    question: string representing the answer asked
    answer: string representing the possible answer
    user: string representing the questions owner
    quantity: integer representing the quantity of stable coin generated
    rate: rate
    """
    state["support"].ask_question(
                question,
                answer,
                user,
                quantity,
                rate,
                auction_end_date,
                market_end_date
            )

@app.command()
def fund_stablecoin(
        value: int = typer.Option(10000000000000000000)
    ):
    """
    fund all accounts with a random quantity of tezos

    value: the amont of tezos funded
    """
    for user in accounts.names():
        print(f"Transferring to {user}")
        state["support"].transfer_stablecoin_to_user(
            user,
            value,
        )
        sleep(60)

@app.command()
def transfer_stablecoin(
        dest: str,
        value: int = typer.Option(100000000000000000)
    ):
    """
    transfer a certain amount of coins toward an user address

    dest: user address that will receive the funds
    """
    state["support"].transfer_stablecoin_to_user(dest, value)

@app.command()
def bid_auction(
        ipfs_hash: str,
        user: str,
        quantity: int = typer.Option(50000),
        rate: int = typer.Option(random.randint(1,99) * PERCENT)
    ):
    """
    launch a bid on an auction

    ipfs_hash: the contract concerned by the bid
    user: string representing the user which is bidding during the auction
    quantity: Integer representing quantity of stable coins bid during the auction
    rate: What is rate?
    """
    state["support"].bid_auction(ipfs_hash, user, quantity, rate)

@app.command()
def random_bids(
        ipfs_hash: str,
        quantity: int = typer.Option(50000),
        rate: int = typer.Option(random.randint(1,99) * PERCENT)
    ):
    """
    launch random bid on a auction from
    all of the user contained in the accounts.names() folder

    ipfs_hash: Contract on which the bid are made
    """
    if len(accounts.names()) == 0:
        print("Please add some accounts.names() before using this functionality")
    with typer.progressbar(accounts.names()) as progress:
        for user in progress:
            state["support"].bid_auction(
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
    state["support"].close_auction(ipfs_hash, user)

@app.command()
def close_market(
        ipfs_hash: str,
        user: str,
        token_type: bool = typer.Option(True)
    ):
    """
    close the market

    ipfs_hash: the hash of the concerned market
    token_type: type of the token
    user: owner of the market
    """
    state["support"].close_market(
            ipfs_hash,
            token_type,
            user
    )

@app.callback()
def main(
        import_accounts: Optional[List[str]] = typer.Option(None)
    ):
    """
    High level option for the tool
    """
    if import_accounts != None:
        for account in import_accounts:
           account_name = typer.prompt("Please associate a name for this account")
           state["accounts"].import_from_file(account, account_name)
           typer.echo(f"{account_name} was imported")
    state['support'] = Support(state["accounts"], config_file="./oracle.ini")
    print(state)

if __name__ == "__main__":
    app()
