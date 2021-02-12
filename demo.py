#!/usr/bin/env python3

"""
Tooling for prediction markets support
"""

import json
import os
import random
import subprocess
import time
from datetime import datetime, timedelta

import configparser
import ipfshttpclient
import pytz
import typer
from pytezos import pytezos

##### Local Script
import summary
from support import Support


##################
# Setup
##################
app = typer.Typer()
config = configparser.ConfigParser()
config.read('oracle.ini')
pm_contract = pytezos.contract(config['Tezos']['pm_contract'])

users = [
    'alice',
    'ava',
    'pascal'
]

PERCENT = 10000000000000000

accounts = {}
pm_contracts = {}

@app.command()
def fund_stablecoin(
        value: int = typer.Option(10000000000000000000)
    ):
    """
    Fund all accounts with a random quantity of tezos

    value: the amont of tezos funded
    """
    for user in users:
        print(f"Transferring to {user}")
        transfer_stablecoin(
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
    Wrapper cli to transfer a certain amount of coins toward an user address

    dest: user address that will receive the funds
    """
    Support.transfer_stablecoin(dest, value)

@app.command()
def bid_auction(
        ipfs_hash: str,
        user: str,
        quantity: int = typer.Option(50000),
        rate: int = typer.Option(random.randint(1,99) * PERCENT)
    ):
    """
    Typer Wrapper to Launch a bid on an auction

    ipfs_hash: the contract concerned by the bid
    user: string representing the user which is bidding during the auction
    quantity: Integer representing quantity of stable coins bid during the auction
    rate: What is rate?
    """
    Support.bid_auction(ipfs_hash, user, quantity, rate)

@app.command()
def random_bids(
        ipfs_hash: str,
        quantity: int = typer.Option(50000),
        rate: int = typer.Option(random.randint(1,99) * PERCENT)
    ):
    """
    Wrapper to launch random bid on a auction from
    all of the user contained in the users folder

    ipfs_hash: Contract on which the bid are made
    """
    if len(users) == 0:
        print("Please add some users before using this functionality")
    with typer.progressbar(users) as progress:
        for user in progress:
            Support.bid_auction(
                ipfs_hash,
                user,
                quantity,
                rate
            )


@app.command()
def close_auction(ipfs_hash: str):
    """
    Wrapper for close the auction

    ipfs_hash: the hash of the concerned contract
    """
    Support.close_auction(ipfs_hash)

if __name__ == "__main__":
    app()
