import pytest
from pytezos import Key

from src.accounts import Accounts

test_accounts = [
    ('donald', 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2'),
    ('clara', 'tz1VA8Y5qDr2yR5kVLhhWd9mkGB1kx7qBrPx'),
    ('mala', 'tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3'),
]



@pytest.mark.parametrize("input,key", test_accounts)
def test_user_is_imported_from_folder(input, key, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_folder("tests/users")
    assert input in accounts


@pytest.mark.parametrize("input,key", test_accounts)
def test_user_is_imported_from_file(input, key, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    assert input in accounts


@pytest.mark.parametrize("name,pbkey", test_accounts)
def test_users_is_imported_to_tezos_client(name, pbkey, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{name}.json", name)
    accounts.import_to_tezos_client(name)
    key = Key.from_alias(name)
    assert key.public_key_hash() == pbkey


@pytest.mark.parametrize("input,key",
                         test_accounts
                         )
def test_users_is_imported_from_tezos_client(input, key, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    accounts2 = Accounts(config["endpoint"])
    accounts2.import_from_tezos_client()
    assert input in accounts2


@pytest.mark.parametrize("input,key",
                         test_accounts
                         )
def test_user_is_activated(input, key, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    accounts.activate_account(input)
    assert accounts[input].balance() > 0


@pytest.mark.parametrize("input,key",
                         test_accounts
                         )
def test_user_is_revealed(input, key, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    accounts.activate_account(input)
    accounts.reveal_account(input)
