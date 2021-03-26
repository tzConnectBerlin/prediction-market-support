import random
import sys
from datetime import datetime, timedelta
from time import sleep

import configparser
import pytest
from decimal import Decimal
from pytezos import pytezos, Key
from typer.testing import CliRunner


from src.accounts import Accounts
from src.config import Config
from src.market import Market
from cli import app

config = Config(config_file="tests/oracle.ini")

def new_market(account):
    test_accounts = Accounts(endpoint=config["endpoint"])
    test_accounts.import_from_folder("tests/users")
    test_accounts.reveal_account(account["name"])
    new_market = Market(test_accounts, config)
    return new_market

accounts = [
        {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"}
]

questions = [
        ["who", "why", "donald", 300, 50, 0.1, 0.2],
        ["who", "why", "donald", 300, 50, 1, 2]
]

test_data = [
    (accounts[0], new_market(accounts[0]), questions[0])
]

client = config["admin_account"]
contract = client.contract(config["contract"])
stablecoins = client.contract(contract.storage["stablecoin"]())

runner = CliRunner()

def rand(mul=100):
    return random.randint(1,99) * mul

def finance_account(key: str):
    client = pytezos.using(
            shell= config["endpoint"],
            key="edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq"
    )
    client.transaction(key, amount=Decimal(10)) \
        .autofill().sign().inject()
    sleep(3)

app_options = [
        "--config-file", "tests/oracle.ini"
]

@pytest.mark.parametrize("account", accounts)
def test_fund_stablecoin(account):
    finance_account(account["key"])
    balance = stablecoins.storage["ledger"][account["key"]]()
    result = runner.invoke(app, app_options + ["fund-stablecoin"])
    print(balance)
    sleep(10)
    new_balance = stablecoins.storage["ledger"][account["key"]]()
    assert stablecoins.storage["ledger"][account["key"]]()
    assert balance["balance"] < new_balance["balance"]

@pytest.mark.parametrize("account", accounts)
def test_transfer_stablecoin(account):
    finance_account(account["key"])
    balance = stablecoins.storage["ledger"][account["key"]]()
    result = runner.invoke(app, app_options + ["transfer-stablecoin", account["name"]])
    print(result.stdout)
    sleep(10)
    new_balance = stablecoins.storage["ledger"][account["key"]]()
    assert stablecoins.storage["ledger"][account["key"]]()
    assert balance["balance"] < new_balance["balance"]

@pytest.mark.parametrize("account,market,data", test_data)
def test_ask_question(account, market, data):
    finance_account(account["key"])
    #make sure only string are passed to the runner
    question_data = list(map(str, data))
    result = runner.invoke(app, app_options + ["ask-question"] + question_data)
    #I take the second one to ensure the ipfs_hash is taken. A regex could be used here
    ipfs_hash = result.stdout.split()[2]

    auction_end = datetime.timestamp(datetime.now() + timedelta(minutes=data[5]))
    market_close = datetime.timestamp(datetime.now() + timedelta(minutes=data[6]))
    sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    assert result.exit_code == 0
    assert question['total_auction_quantity'] == data[3]
    assert question['state'] == "questionAuctionOpen"
    assert question['owner'] == account["key"]
    assert question['auction_end'] == int(auction_end)
    assert question['market_close'] == int(market_close)

@pytest.mark.parametrize("account,market,data", test_data)
def test_bid_auction(account, market, data):
    finance_account(account["key"])
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    result = runner.invoke(app, app_options + ["bid-auction", account["name"]])
    sleep(3)
    bids = question["auction_bids"]
    assert account["key"] in bids

@pytest.mark.parametrize("account,market,data", test_data)
def test_close_auction(account, market, data):
    finance_account(account["key"])
    sleep(3)
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    sleep(data[5] * 60 + 60)
    result = runner.invoke(app, app_options + ["close-auction", ipfs_hash, account["name"]])
    sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionAuctionWithdrawOpen"

@pytest.mark.parametrize("account,market,data", test_data)
def test_close_market(account,market,data):
    finance_account(account["key"])
    sleep(3)
    ipfs_hash = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    result = runner.invoke(app, app_options + ["close-market", ipfs_hash, account["name"]])
    sleep(data[6] * 60 + 60)
    question = contract.storage["questions"][ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionMarketClosed"
