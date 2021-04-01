# content of conftest.py
import os
import pytest

from decimal import Decimal
from pytezos import pytezos
from time import sleep

from src.accounts import Accounts
from src.config import Config
from src.deploy import deploy_market
from src.market import Market


def mock_get_tezos_client_path():
    return os.path.join('tests/users', 'secret_keys')


@pytest.fixture(autouse=True)
def mock_functions(monkeypatch):
    monkeypatch.setattr(
        # api_call is from slow.py but imported to main.py
        'src.utils.get_tezos_client_path',
        lambda  x: mock_get_tezos_client_path
    )


@pytest.fixture(scope="session")
def accounts():
    accounts = [
        {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"}
    ]
    return accounts

@pytest.fixture(scope="session", autouse=True)
def contract_id():
    return deploy_market()

@pytest.fixture(scope="session", autouse=True)
def config(contract_id):
    config = Config(config_file="tests/oracle.ini", contract=contract_id)
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
def stablecoin_storage(client, config):
    contract = client.contract(config['contract'])
    stablecoin = client.contract(contract.storage['stablecoin']())
    return stablecoin.storage['ledger']


@pytest.fixture(scope="session", autouse=True)
def questions_storage(client, config):
    contract = client.contract(config['contract'])
    return contract.storage['questions']


@pytest.fixture(scope="session", autouse=True)
def finance_accounts(client, accounts, config: Config):
    for account in accounts:
        client.transaction(
            account['key'], amount=Decimal(10)
        ).autofill().sign().inject()
    sleep(3)


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    #launch_sandbox()
    


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
    called before test process is exited.
    """
    #stop_sandbox()
