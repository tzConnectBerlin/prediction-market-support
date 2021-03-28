import pytest
from pytezos import Key

from src.accounts import Accounts

test_accounts = [
    ('donald', 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2')
]

@pytest.mark.parametrize("input", ["donald"])
def test_user_is_imported_from_folder(input, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_folder("tests/users")
    assert "donald" in accounts


@pytest.mark.parametrize("input", ["donald"])
def test_user_is_imported_from_file(input, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    assert input in accounts


@pytest.mark.parametrize("name,key", test_accounts)
def test_users_is_imported_to_tezos_client(name, key, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{name}.json", name)
    accounts.import_to_tezos_client(name)
    key = Key.from_alias(name)
    assert key.public_key_hash() == key


@pytest.mark.parametrize("input", ["donald"])
def test_users_is_imported_from_tezos_client(input, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    accounts2 = Accounts(config["endpoint"])
    accounts2.import_from_tezos_client()
    assert input in accounts2


@pytest.mark.parametrize("input,key",
    test_accounts
)
def test_user_is_activated(input,key, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    accounts.activate_account(input)
    assert accounts[input].balance() > 0



@pytest.mark.parametrize("input,key",
    test_accounts
)
def test_user_is_revealed(input,key, config):
    accounts = Accounts(config["endpoint"])
    accounts.import_from_file(f"tests/users/{input}.json", input)
    accounts.activate_account(input)
    accounts.reveal_account(input)


@pytest.mark.parametrize("input,contract_id", [
])
def test_get_accounts(input, contract_id, config):
    accounts = Accounts(config["endpoint"])
    contract = accounts.contract_accounts(contract_id)
