import random
from datetime import datetime, timedelta
from time import sleep

import pytest
from typer.testing import CliRunner

from cli import app

#accounts used for test
accounts = [
    {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"},
    {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3"}
]

#questions data to test functions
questions = [
    ["who", "why", "donald", 300, 50, 0.1, 0.2],
    ["who", "why", "mala", 300, 50, 1, 2],
]


#testdata mix for easier use a parametrised
test_data = [
    (accounts[0], questions[0]),
    (accounts[1], questions[1]),
]

runner = CliRunner()

def rand(mul=100):
    return random.randint(1, 99) * mul

app_options = [
        "--config-file", "tests/cli.ini", "--contract"
]


@pytest.mark.parametrize("account", accounts)
def test_list_accounts(account, contract_id):
    result = runner.invoke(app, app_options + [contract_id] + ["list-accounts"])
    assert account['name'] in result.stdout


"""
@pytest.mark.parametrize("account,data", test_data)
def test_ask_question(account, market, data, questions_storage, contract_id):
    #make sure only string are passed to the runner
    question_data = list(map(str, data))
    result = runner.invoke(app, app_options + [contract_id] + ["ask-question"] + question_data)
    #I take the second one to ensure the ipfs_hash is taken. A regex could be used here
    ipfs_hash = list(filter(lambda x: x.startswith('Qm'), result.stdout.split()))

    auction_end = datetime.timestamp(datetime.now() + timedelta(minutes=data[5]))
    market_close = datetime.timestamp(datetime.now() + timedelta(minutes=data[6]))
    sleep(3)
    question = questions_storage[ipfs_hash[0]]()
    assert result.exit_code == 0
    assert question['total_auction_quantity'] == data[3]
    assert question['state'] == "questionAuctionOpen"
    assert question['owner'] == account["key"]
    assert question['auction_end'] <= int(auction_end) + 1
    assert question['market_close'] <= int(market_close) + 1


@pytest.mark.parametrize("account", accounts)
def test_fund_stablecoin(account, stablecoin_storage, contract_id):
    balance = stablecoin_storage[account["key"]]()
    runner.invoke(app, app_options + [contract_id] + ["fund-stablecoin"])
    sleep(6)
    new_balance = stablecoin_storage[account["key"]]()
    assert stablecoin_storage[account["key"]]()
    assert balance["balance"] < new_balance["balance"]


@pytest.mark.parametrize("account", accounts)
def test_transfer_stablecoin(account, stablecoin_storage, contract_id):
    balance = stablecoin_storage[account["key"]]()
    runner.invoke(app, app_options + [contract_id] + ["transfer-stablecoin", account["name"]])
    sleep(6)
    new_balance = stablecoin_storage[account["key"]]()
    assert stablecoin_storage[account["key"]]()
    assert balance["balance"] < new_balance["balance"]


@pytest.mark.parametrize("account,data", test_data)
def test_bid_auction(account, market, data, questions_storage, contract_id):
    ipfs_hash = market.ask_question(data[0], data[1], account["name"], data[3], data[4], data[5], data[6])
    sleep(3)
    question = questions_storage[ipfs_hash]()
    runner.invoke(app, app_options + [contract_id] + ["bid-auction", account["name"]])
    sleep(3)
    bids = question["auction_bids"]
    assert account["key"] in bids


@pytest.mark.parametrize("account,data", test_data)
def test_close_auction(account, market, data, questions_storage, contract_id):
    ipfs_hash = market.ask_question(data[0], data[1], account["name"], data[3], data[4], data[5], data[6])
    sleep(data[5] * 60 + 60)
    runner.invoke(app, app_options + [contract_id] + ["close-auction", ipfs_hash, account["name"]])
    sleep(3)
    question = questions_storage[ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionAuctionWithdrawOpen"


@pytest.mark.parametrize("account,data", test_data)
def test_close_market(account, market, data, questions_storage, contract_id ):
    ipfs_hash = market.ask_question(data[0], data[1], account["name"], data[3], data[4], data[5], data[6])
    sleep(data[6] * 60 + 20)
    runner.invoke(app, app_options + [contract_id] + ["close-market", ipfs_hash, account["name"]])
    sleep(data[6] * 60 + 20)
    question = questions_storage[ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionMarketClosed"
"""
