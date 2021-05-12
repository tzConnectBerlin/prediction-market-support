import pytest
from pytezos import Key

from src.accounts import Accounts

test_accounts = [
    ('rimk', 'tz1PMqV7qGgWMNH2HR9inWjSvf3NwtHg7Xg4'),
    ('tang', 'tz1MDwHYDLgPydL5iav7eee9mZhe6gntoLet'),
    ('patoch', 'tz1itzGH43N8Y9QT1UzKJwJM8Y3qK8uckbXB'),
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
