import random
import sys
import time

import configparser
import pytest
from decimal import Decimal
from pytezos import pytezos, Key

from src.accounts import Accounts
from src.utils import summary

config_file="./tests/oracle.ini"
config = configparser.ConfigParser()
config.read(config_file)

client = pytezos.using(
        shell=config["Tezos"]["endpoint"],
        key=config["Tezos"]["privkey"]
)

def finance_account(user: str):
    client.transaction("tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", amount=Decimal(3)) \
            .autofill().sign().inject()
    time.sleep(3)

def test_user_is_imported_from_folder():
    accounts = Accounts("http://localhost:20000", folder="tests/users")
    accounts.import_from_folder("tests/users")

def test_user_is_imported_from_file():
    accounts = Accounts("http://localhost:20000", folder=None)
    accounts.import_from_file("tests/users/donald.json", "donald")
    assert accounts["donald"] != None

def test_users_is_imported_to_tezos_client():
    accounts = Accounts("http://localhost:20000", "tests/users")
    accounts.import_to_tezos_client("donald")
    key = Key.from_alias("donald")
    assert key.public_key_hash() == "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"
    assert key.public_key() == "edpktqDLAmhcUAbztjBP7v8fyj5NGWU1G47kZrpvBY19TMLgjFRovR"
    assert key.secret_key() == "edsk2sRikkzrGKnRC28UhvJsKAM19vuv4LtCRViyjkm2jMyAxiCMuG"

def test_users_is_imported_from_tezos_client():
    accounts = Accounts("http://localhost:20000", "tests/users")
    accounts.import_from_tezos_client("donald")
    key = Key.from_alias("donald")
    assert key.public_key_hash() == "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"
    assert key.public_key() == "edpktqDLAmhcUAbztjBP7v8fyj5NGWU1G47kZrpvBY19TMLgjFRovR"
    assert key.secret_key() == "edsk2sRikkzrGKnRC28UhvJsKAM19vuv4LtCRViyjkm2jMyAxiCMuG"

def test_user_is_activated():
    finance_account("donald")
    accounts = Accounts("http://localhost:20000", folder="tests/users")
    accounts.activate_account("donald")
    account = accounts.get_account("donald")
    assert account.balance() > 0

def test_user_is_revealed():
    finance_account("donald")
    accounts = Accounts("http://localhost:20000", folder="tests/users")
    accounts.activate_account("donald")
    accounts.reveal_account("donald")

def test_get_accounts():
    accounts = Accounts("http://localhost:20000", folder="tests/users")
    accounts.get_account("donald")
