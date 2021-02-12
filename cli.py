#!/usr/bin/env python3

"""
Tooling for prediction markets support
"""

import json
import random

import configparser
import typer

##### Local Script
import summary
from support import Support, transfer_stablecoin

PERCENT = 10000000000000000

##################
# Setup
##################
users = [
    'alice',
    'ava',
    'pascal'
]

app = typer.Typer()

support = Support(users)

@app.command()
def manage_accounts(
        activate: bool = typer.Option(False, "--activate", "-a"),
        reveal: bool = typer.Option(False, "--reveal", "-r"),
        import_accounts: bool = typer.Option(False, "--import", "-i")
        ):
    """
    management of accounts in the user folder
    """
    with typer.progressbar(users) as progress:
        for user in progress:
            if import_accounts:
                support.import_user(user)
            if activate:
                support.activate_user(user)
            if reveal:
                support.reveal_user(user)
            print("\n")

@app.command()
def ask_question(
        question: str,
        answer: str,
        user: str,
        quantity: int = typer.Option(50000),
        rate: int = typer.Option(random.randint(1,99) * PERCENT)
    ):
    """
    create a question in IPFS

    question: string representing the answer asked
    answer: string representing the possible answer
    user: string representing the questions owner
    quantity: integer representing the quantity of stable coin generated
    rate: rate
    """
    support.ask_question(
                question,
                answer,
                user,
                quantity,
                rate
            )

@app.command()
def fund_stablecoin(
        value: int = typer.Option(10000000000000000000)
    ):
    """
    fund all accounts with a random quantity of tezos

    value: the amont of tezos funded
    """
    for user in users:
        print(f"Transferring to {user}")
        support.transfer_stablecoin_to_user(
            user,
            value,
        )
        time.sleep(60)

@app.command()
def transfer_stablecoin(
        dest: str,
        value: int = typer.Option(100000000000000000)
    ):
    """
    transfer a certain amount of coins toward an user address

    dest: user address that will receive the funds
    """
    support.transfer_stablecoin(dest, value)

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
    support.bid_auction(ipfs_hash, user, quantity, rate)

@app.command()
def random_bids(
        ipfs_hash: str,
        quantity: int = typer.Option(50000),
        rate: int = typer.Option(random.randint(1,99) * PERCENT)
    ):
    """
    launch random bid on a auction from
    all of the user contained in the users folder

    ipfs_hash: Contract on which the bid are made
    """
    if len(users) == 0:
        print("Please add some users before using this functionality")
    with typer.progressbar(users) as progress:
        for user in progress:
            support.bid_auction(
                ipfs_hash,
                user,
                quantity,
                rate
            )

@app.command()
def close_auction(ipfs_hash: str):
    """
    close the auction

    ipfs_hash: the hash of the concerned contract
    """
    support.close_auction(ipfs_hash)

if __name__ == "__main__":
    app()
