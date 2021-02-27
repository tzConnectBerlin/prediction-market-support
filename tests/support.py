import random
import sys
import time

import configparser
import pytest
from decimal import Decimal
from pytezos import pytezos, Key

from src.support.support import Support
from src.utils import summary

config_file="./tests/oracle.ini"
support_instance = Support(
        ["donald"],
        config_file=config_file,
        user_folder="./tests/users"
)
config = configparser.ConfigParser()
config.read(config_file)

client = pytezos.using(
        shell=config["Tezos"]["endpoint"],
        key=config["Tezos"]["privkey"]
)

contract = client.contract(config["Tezos"]["pm_contract"])
stablecoins = client.contract(contract.storage["stablecoin"]())

def rand():
    return random.randint(1,99)

def finance_account(user: str):
    client.transaction("tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", amount=Decimal(3)) \
            .autofill().sign().inject()
    time.sleep(3)

def test_users_is_imported():
    support_instance.import_user("donald")
    key = Key.from_alias("donald")
    assert key.public_key_hash() == "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"
    assert key.public_key() == "edpktqDLAmhcUAbztjBP7v8fyj5NGWU1G47kZrpvBY19TMLgjFRovR"
    assert key.secret_key() == "edsk2sRikkzrGKnRC28UhvJsKAM19vuv4LtCRViyjkm2jMyAxiCMuG"

def test_user_is_activated():
    support_instance.activate_user("donald")
    account = support_instance.get_account("donald")
    assert account.balance() > 0

def test_user_is_revealed():
    finance_account("donald")
    support_instance.reveal_user("donald")
    #test with simple operation if user revealed somewhere

def test_get_user_account():
    account = support_instance.get_account("donald")
    assert account.key.public_key_hash() == "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"

def test_fund_stablecoin():
    finance_account("donald")
    support_instance.transfer_stablecoin_to_user("donald", rand() * 100)
    time.sleep(3)
    balance = stablecoins.storage["ledger"]["tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"]()
    amount = rand() * 100
    support_instance.transfer_stablecoin_to_user("donald", amount)
    time.sleep(3)
    new_balance = stablecoins.storage["ledger"]["tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"]()
    assert stablecoins.storage["ledger"]["tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"]()
    assert balance["balance"] + amount == new_balance["balance"]

def test_ask_question():
    finance_account("donald")
    ipfs_hash = support_instance.ask_question("wco", "wpy", "donald", 300, 50, 30, 50)
    time.sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    assert question['total_auction_quantity'] == 300
    assert question['state'] == "questionAuctionOpen"
    assert question['owner'] == "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"    #check timestamps

def test_bid_auction():
    finance_account("donald")
    ipfs_hash = support_instance.ask_question("who", "why", "donald", 300, 50, 30, 50)
    time.sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    support_instance.bid_auction(ipfs_hash, "donald", 100, 10)
    time.sleep(3)
    bids = question["auction_bids"]
    assert "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2" in bids

def test_close_auction():
    finance_account("donald")
    time.sleep(3)
    ipfs_hash = support_instance.ask_question("whl", "wha", "donald", 300, 50, 1, 2)
    time.sleep(80)
    support_instance.close_auction(ipfs_hash, "donald")
    time.sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionAuctionWithdrawOpen"

def test_close_market():
    finance_account("donald")
    time.sleep(3)
    ipfs_hash = support_instance.ask_question("whl", "wha", "donald", 300, 50, 1, 2)
    time.sleep(130)
    support_instance.close_market(ipfs_hash, True, "donald")
    time.sleep(3)
    question = contract.storage["questions"][ipfs_hash]()
    auction_state = question["state"]
    assert auction_state == "questionMarketClosed"

def test_buy_token():
    finance_account("donald")
    ipfs_hash = support_instance.ask_question("whl", "wha", "donald", 300, 50, 1, 2)
    time.sleep(3)
    balance = stablecoins.storage["ledger"]["tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"]()
    amount = rand() * 100
    support_instance.buy_token(ipfs_hash, True, amount, "donald")
    time.sleep(3)
    new_balance = stablecoins.storage["ledger"]["tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"]()
    assert stablecoins.storage["ledger"]["tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"]()
    assert balance["balance"] - amount == new_balance["balance"]

def test_burn_token():
    finance_account("donald")
    ipfs_hash = support_instance.ask_question("whl", "wha", "donald", 300, 50, 1, 2)
    time.sleep(3)
    balance = stablecoins.storage["ledger"]["tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"]()
    amount = rand() * 100
    support_instance.burn(ipfs_hash, amount, "donald")
    time.sleep(3)
    new_balance = stablecoins.storage["ledger"]["tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"]()
    assert stablecoins.storage["ledger"]["tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"]()
    assert balance["balance"] == new_balance["balance"] + amount
