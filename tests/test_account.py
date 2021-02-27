import random
import sys
import time

import pytest
from decimal import Decimal
from pytezos import pytezos, Key

from src.accounts import Accounts
from src.utils import summary

test_shell="http://localhost:20000"
admin_account_key="edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq"
client = pytezos.using(
        shell=test_shell,
        key=admin_account_key
)


def finance_account(user: str):
    client.transaction("tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", amount=Decimal(3)) \
            .autofill().sign().inject()
    time.sleep(3)

@pytest.mark.parametrize("input", ["donald"])
def test_user_is_imported_from_folder(input):
    accounts = Accounts(test_shell, folder=None)
    accounts.import_from_folder("tests/users")
    assert input in accounts

@pytest.mark.parametrize("input", ["donald"])
def test_user_is_imported_from_file(input):
    accounts = Accounts(test_shell, folder=None)
    accounts.import_from_file(f"tests/users/{input}.json", input)
    assert input in accounts

@pytest.mark.parametrize("input", ["donald"])
def test_users_is_imported_to_tezos_client(input):
    accounts = Accounts(test_shell, "tests/users")
    accounts.import_to_tezos_client(input)
    key = Key.from_alias(input)
    assert key.public_key_hash() == "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"
    assert key.public_key() == "edpktqDLAmhcUAbztjBP7v8fyj5NGWU1G47kZrpvBY19TMLgjFRovR"
    assert key.secret_key() == "edsk2sRikkzrGKnRC28UhvJsKAM19vuv4LtCRViyjkm2jMyAxiCMuG"

@pytest.mark.parametrize("input", ["donald"])
def test_users_is_imported_from_tezos_client(input):
    accounts = Accounts(test_shell, "tests/users")
    accounts.import_from_tezos_client(input)
    assert input in accounts

@pytest.mark.parametrize("input", ["donald"])
def test_user_is_activated(input):
    finance_account(input)
    accounts = Accounts(test_shell, folder="tests/users")
    accounts.activate_account(input)
    assert accounts[input].balance() > 0

@pytest.mark.parametrize("input", ["donald"])
def test_user_is_revealed(input):
    finance_account(input)
    accounts = Accounts(test_shell, folder="tests/users")
    accounts.activate_account(input)
    accounts.reveal_account(input)

@pytest.mark.parametrize("input", ["donald"])
def test_get_accounts(input):
    accounts = Accounts(test_shell, folder="tests/users")
    contract = accounts.contract_accounts(input)
