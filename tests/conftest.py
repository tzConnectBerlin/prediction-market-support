# content of conftest.py
import os
import pytest
import random
from time import sleep, time
from datetime import datetime, timedelta
from decimal import Decimal

from loguru import logger
from pytezos import pytezos

from src.accounts import Accounts
from src.config import Config
from src.compile import launch_sandbox, stop_sandbox
from src.deploy import deploy_market, deploy_stablecoin
from src.market import Market
from src.stablecoin import Stablecoin
from src.utils import *


market_pool = []
accounts_pool = []

logger.add(sys.stdout, colorize=True)
logger.add("tests/test.log", enqueue=True)

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
def test_accounts(config):
    accounts_pool = [
        {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"},
        {"name": "clara", "key": "tz1VA8Y5qDr2yR5kVLhhWd9mkGB1kx7qBrPx", "status": "created"},
        {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"},
        {"name": "marty", "key": "tz1Q3eT3kwr1hfvK49HK8YqPadNXzxdxnE7u", "status": "created"},
        {"name": "palu", "key": "tz1LQn3AuoxRVwBsb3rVLQ56nRvC3JqNgVxR", "status": "created"},
        {"name": "rimk", "key": "tz1PMqV7qGgWMNH2HR9inWjSvf3NwtHg7Xg4", "status": "created"},
        {"name": "tang", "key": "tz1MDwHYDLgPydL5iav7eee9mZhe6gntoLet", "status": "created"},
        {"name": "patoch", "key": "tz1itzGH43N8Y9QT1UzKJwJM8Y3qK8uckbXB", "status": "created"}
    ]
    return accounts_pool


@pytest.fixture(scope="session", autouse=True)
def contract_id():
    id = deploy_market()
    return id


@pytest.fixture(scope="session", autouse=True)
def stablecoin_id():
    id = deploy_stablecoin()
    return id


@pytest.fixture(scope="session", autouse=True)
def config(contract_id, stablecoin_id):
    config = Config(config_file="tests/cli.ini", contract=contract_id, stablecoin=stablecoin_id)
    return config


@pytest.fixture(scope="session", autouse=True)
def market(config):
    test_accounts = Accounts(endpoint=config["endpoint"])
    test_accounts.import_from_folder("tests/users")
    new_market = Market(test_accounts, config)
    return new_market


@pytest.fixture(scope="session", autouse=True)
def stablecoin(config):
    test_accounts = Accounts(endpoint=config["endpoint"])
    test_accounts.import_from_folder("tests/users")
    new_stablecoin = Stablecoin(test_accounts, config)
    return new_stablecoin


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
def ledger_storage(client, config):
    return get_tokens_ledgermap(client, config['contract'])


@pytest.fixture(scope="session", autouse=True)
def supply_storage(client, config):
    return get_tokens_supplymap(client, config['contract'])


@pytest.fixture(scope="session", autouse=True)
def finance_accounts(client, test_accounts, config: Config, stablecoin_id: str):
    money_seeding = []
    stablecoin_seeding = []
    for account in test_accounts:
        money_seed = client.transaction(
            account['key'], amount=Decimal(10)
        )
        account['status'] += ',tezzed'
        money_seeding.append(money_seed)
        stablecoin = get_stablecoin(config['admin_account'], stablecoin_id)
        stablecoin_seed = stablecoin.transfer({
            'from': get_public_key(config['admin_account']),
            'to': account['key'],
            'value': 2 ** 42
        })
        account['status'] += ',financed'
        stablecoin_seeding.append(stablecoin_seed.as_transaction())

    bulk_transactions = config["admin_account"].bulk(*(stablecoin_seeding + money_seeding))
    submit_transaction(bulk_transactions, error_func=print_error)
    sleep(3)
    return test_accounts


@pytest.fixture(scope="session", autouse=True)
def revealed_accounts(test_accounts, config):
    accounts_obj = Accounts(config["endpoint"])
    accounts_to_reveal = random.choices(test_accounts, k=4)
    for account in accounts_to_reveal:
        accounts_obj.import_from_file(f"tests/users/{account['name']}.json", account['name'])
        #accounts_obj.activate_account(account['name'])
        #accounts_obj.reveal_account(account['name'])
        account["status"] = "revealed"
    return accounts_to_reveal


@pytest.fixture(scope="session")
def gen_markets(revealed_accounts, config, market, stablecoin_id):
    transactions = []
    reserved = []
    print("generating markets")
    for i in range(2):
        for index in range(40):
            quantity = random.randint(0, 900)
            rate = random.randint(0, 2 ** 63)
            end_delay = random.uniform(0.2, 0.5)
            end = datetime.now() + timedelta(end_delay)
            name = random.choice(revealed_accounts)['name']
            market_id, transaction = market.ask_question(
                id_generator(),
                id_generator(),
                name,
                quantity,
                rate,
                "dededededede",
                auction_end_date=end.timestamp(),
                token_contract=stablecoin_id
            )
            if market_id not in reserved:
                reserved.append(market_id)
                transactions.append(transaction)
                market_pool.append({
                    'id': int(market_id),
                    'caller_name': name,
                    'end': end,
                    'status': 'created'
                })
        bulk_transactions = config["admin_account"].bulk(*transactions)
        submit_transaction(bulk_transactions, error_func=print_error)
        sleep(2)
        transactions.clear()
    logger.debug(f'reserved size is {len(reserved)}')
    logger.debug(f'reserved size is {market_pool}')
    print("markets generated")
    return market_pool


@pytest.fixture(scope="session")
def gen_bid_markets(gen_markets, market):
    selection = random.sample(gen_markets, k=60)
    for i in range(1):
        for ma in selection:
            ma['status'] = 'bidded'
            bulk_transactions = market.multiple_bids(
                ma['id'],
                random.randint(2, 2 ** 8),
                random.randint(2, 2 ** 63)
            )
        submit_transaction(bulk_transactions, error_func=print_error)
        sleep(2)
    return selection


@pytest.fixture(scope="session", autouse=True)
def gen_cleared_markets(config, market, gen_bid_markets):
    sleep(60)
    selection = random.sample(gen_bid_markets, k=40)
    cleared = []
    logger.debug("in function gen cleared markets")
    for ma in selection:
        transaction = market.auction_clear(ma['id'], ma['caller_name'])
        try:
            submit_transaction(transaction, error_func=raise_error)
            ma['status'] = 'cleared'
            cleared.append(ma)
        except Exception as e:
            logger.debug(e)
            continue
    sleep(2)
    logger.debug(len(cleared))
    return cleared


@pytest.fixture(scope="function", autouse=True)
def log_contract_state(contract_id):
    logger.debug("___________________")
    #f"{caller_tez_balance} {stablecoin_balance}"
    yield logger
    logger.debug("___________________")


def get_random_market(status='created'):
    pool = [x for x in market_pool if status == x['status']]
    logger.error(pool)
    return random.choice(pool)


def pytest_configure():
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    #launch_sandbox()
    #sleep(20)


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


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    start = time()
    yield
    total = time() - start
    logger.error(total)


