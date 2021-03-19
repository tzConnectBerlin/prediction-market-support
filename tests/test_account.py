import random
import sys
import time

import pytest
from decimal import Decimal
from pytezos import pytezos, Key

from src.accounts import Accounts
from src.config import Config
from src.utils import summary

config = Config(config_file="tests/oracle.ini")

def finance_account(key: str):
    client = config["admin_account"]
    client.transaction(key, amount=Decimal(100)) \
            .autofill().sign().inject()
    time.sleep(3)

#Get a fixture of all accounts
#Get a mock for the tezos-client folder
@pytest.mark.parametrize("input", ["donald"])
def test_user_is_imported_from_folder(input):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_folder("tests/users")
    assert "donald" in accounts

@pytest.mark.parametrize("input", ["donald"])
def test_user_is_imported_from_file(input):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    assert input in accounts

@pytest.mark.parametrize("input", ["donald"])
def test_users_is_imported_to_tezos_client(input):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    accounts.import_to_tezos_client(input)
    key = Key.from_alias(input)
    assert key.public_key_hash() == "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"
    assert key.public_key() == "edpktqDLAmhcUAbztjBP7v8fyj5NGWU1G47kZrpvBY19TMLgjFRovR"
    assert key.secret_key() == "edsk2sRikkzrGKnRC28UhvJsKAM19vuv4LtCRViyjkm2jMyAxiCMuG"

@pytest.mark.parametrize("input", ["donald"])
def test_users_is_imported_from_tezos_client(input):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    accounts2 = Accounts(config["endpoint"])
    accounts2.import_from_tezos_client()
    assert input in accounts2

@pytest.mark.parametrize("input,key", [
    ("donald", "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2")
])
def test_user_is_activated(input,key):
    finance_account(key)
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    accounts.activate_account(input)
    assert accounts[input].balance() > 0

@pytest.mark.parametrize("input,key", [
    ("donald", "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2")
 ])
def test_user_is_revealed(input,key):
    finance_account(key)
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    accounts.activate_account(input)
    accounts.reveal_account(input)

@pytest.mark.parametrize("input,contract_id", [
    ("donald", config["contract"])
])
def test_get_accounts(input, contract_id):
    accounts = Accounts(config["endpoint"])
    contract = accounts.contract_accounts(contract_id)
