# content of conftest.py
import os
import pytest

from decimal import Decimal
from pytezos import pytezos
from time import sleep

from src.accounts import Accounts
from src.config import Config
from src.compile import launch_sandbox, stop_sandbox
from src.deploy import deploy_market, deploy_stablecoin
from src.market import Market
from src.utils import get_stablecoin, get_public_key, get_market_map, get_question_liquidity_provider_map


def mock_get_tezos_client_path():
    return os.path.join('tests/users', 'secret_keys')


@pytest.fixture(scope='function', autouse=True)
def mock_functions(monkeypatch):
    print("mock_function")
    monkeypatch.setattr(
        'src.utils.get_tezos_client_path',
        lambda: os.path.join('tests/users', 'secret_keys')
    )


@pytest.fixture(scope="session")
def accounts():
    accounts = [
        {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"},
        {"name": "clara", "key": "tz1VA8Y5qDr2yR5kVLhhWd9mkGB1kx7qBrPx"},
        {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3"},
        {"name": "marty", "key": "tz1Q3eT3kwr1hfvK49HK8YqPadNXzxdxnE7u"},
        {"name": "palu", "key": "tz1LQn3AuoxRVwBsb3rVLQ56nRvC3JqNgVxR"}
    ]
    return accounts


@pytest.fixture(scope="session", autouse=True)
def contract_id():
    return deploy_market()


def stablecoin_id():
    return deploy_stablecoin()


@pytest.fixture(scope="session", autouse=True)
def config(contract_id):
    config = Config(config_file="tests/cli.ini", contract=contract_id, stablecoin=stablecoin_id)
    return config


@pytest.fixture(scope="session", autouse=True)
def market(config):
    test_accounts = Accounts(endpoint=config["endpoint"])
    test_accounts.import_from_folder("tests/users")
    new_market = Market(test_accounts, config)
    return new_market


@pytest.fixture(scope="session", autouse=True)
def client(config):
    client = pytezos.using(
        shell=config["endpoint"],
        key="edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq"
    )
    return client


@pytest.fixture(scope="session", autouse=True)
def stablecoin_storage(client, stablecoin_id):
    stablecoin = client.contract(stablecoin_id)
    return stablecoin.storage['ledger']


@pytest.fixture(scope="session", autouse=True)
def questions_storage(client, config):
    return get_market_map(client, config['contract'])


@pytest.fixture(scope="session", autouse=True)
def liquidity_storage(client, config):
    return get_question_liquidity_provider_map(client, config['contract'])


@pytest.fixture(scope="session", autouse=True)
def finance_accounts(client, accounts, config: Config, contract_id: str):
    for account in accounts:
        client.transaction(
            account['key'], amount=Decimal(10)
        ).autofill().sign().inject()

        #modify that part to get the stablecoin
        stablecoin = get_stablecoin(config['admin_account'], contract_id)

        stablecoin.transfer({
            'from': get_public_key(config['admin_account']),
            'to': account['key'],
            'value': 100000
        }).as_transaction().autofill().sign().inject()
    sleep(3)


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    #launch_sandbox()
    #sleep(70)
    


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    #launch_sandbox()


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """


def pytest_unconfigure(config):
    """
    Called before test process is exited.
    """
    #stop_sandbox()