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
reserved = []

test_accounts = [
    {"name": "donald", "key": "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2", "status": "created"},
    {"name": "mala", "key": "tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3", "status": "created"},
    {"name": "marty", "key": "tz1Q3eT3kwr1hfvK49HK8YqPadNXzxdxnE7u", "status": "created"},
    {"name": "palu", "key": "tz1LQn3AuoxRVwBsb3rVLQ56nRvC3JqNgVxR", "status": "created"},
    {"name": "rimk", "key": "tz1PMqV7qGgWMNH2HR9inWjSvf3NwtHg7Xg4", "status": "created"},
    {"name": "tang", "key": "tz1MDwHYDLgPydL5iav7eee9mZhe6gntoLet", "status": "created"},
    {"name": "patoch", "key": "tz1itzGH43N8Y9QT1UzKJwJM8Y3qK8uckbXB", "status": "created"},
    {"name": "marco", "key": "tz1UbdPPEVcyT5tC34yh7LweQ1tTWk8vHVXk", "status": "created"},
    {"name": "carl", "key": "tz1XvHb5KDrui5S8WJP6txdAG7Qu5WHbfw1Q", "status": "created"},
    {"name": "siri", "key": "tz1MT1ZfNoDXzWvUj4zJg8cVq7tt7a6QcC58", "status": "created"},
    {"name": "clara", "key": "tz1dWWkzwEKWg9S7sA3A2gFcZXzyz3ekHNRE", "status": "created"},
    {"name": "lisa", "key": "tz1SVMjM4BcELyhBYhqUVe5PaV2ZgckBd8bG", "status": "created"},
    {"name": "laura", "key": "tz1P6AVBYU3SAz6o9gCAxpgLG3TsF7mSLTk7", "status": "created"},
    {"name": "anna", "key": "tz1UZFiTE2G5vxRicUeiyov5yt6Zku6fC3dt", "status": "created"},
    {"name": "maria", "key": "tz1NY2EdxiVNyyB5kLAiZCC1UrA6CagM5Zek", "status": "created"},
    {"name": "penny", "key": "tz1UGtuFY8R3fQp6Exi9Bb6AMppVubunFj2p", "status": "created"},
    {"name": "amy", "key": "tz1TXa1B9CfMmvWPH7uWX3rsjNcqzLZ6af5U", "status": "created"},
    {"name": "astrid", "key": "tz1SopWRnn116FzCevsZxL9rzpJq4A6hFWRv", "status": "created"},
    {"name": "cathalina", "key": "tz1hNY9Fv11hNZBwmjRe4VtTwkeevgW6tGq9", "status": "created"},
    {"name": "romina", "key": "tz1iFcpVuaBCaffFNG8LZKJrQdzzj7c5uW3t", "status": "created"},
    {"name": "xenia", "key": "tz1L5nZbXTV46KGVB4gRVNQ4RWxYoq3jLn1R", "status": "created"},
    {"name": "eva", "key": "tz1dAPf4ivAgAQbp7Lua2M7kecVu6d9t4oYJ", "status": "created"},
    {"name": "alexa", "key": "tz1Vb3PvQAHTgyp56rXqSpkcaUc5zdEcFfbD", "status": "created"},
    {"name": "mia", "key": "tz1Lc4SKZLFriSm8ouwyUo3Hxkbv35VxwBP1", "status": "created"},
    {"name": "robin", "key": "tz1XRcA64rrepjkDgJudqjk7Z5HyALk8u9iU", "status": "created"},
    {"name": "hannah", "key": "tz1hGsWjVurdQMR7U9EC8TYwhgubfioTSf28", "status": "created"},
    {"name": "emma", "key": "tz1QahWZZHgrREnjThcxKXdmQMuqAWwYWoB9", "status": "created"},
    {"name": "lily", "key": "tz1bCwYgZcTQwLERvXS9UZghffENphBsEcho", "status": "created"},
    {"name": "madonna", "key": "tz1RncjhUDusSeNoLT11z35wmdRRaMsq5fsp", "status": "created"},
    {"name": "nina", "key": "tz1ZJARU2TodXW8cFhYuai3VmLpY1qqkHq9B", "status": "created"},
    {"name": "robert", "key": "tz1ghjxBNM1ic25Lzq33Eq7z5RiXTQhiaPDT", "status": "created"},
    {"name": "tasos", "key": "tz1XdPirP3FxZDNGZMhw7Nk2hDAfSiCVGWF9", "status": "created"},
    {"name": "sergio", "key": "tz1gK1rZy2Biut8hcJiyEufbtXQ9rkNvToub", "status": "created"},
    {"name": "stavros", "key": "tz1iPFr4obPeSzknBPud8uWXZC7j5gKoah8d", "status": "created"},
    {"name": "leonidas", "key": "tz1ZrWi7V8tu3tVepAQVAEt8jgLz4VVEEf7m", "status": "created"}
]


@pytest.fixture(scope="session", autouse=True)
def contract_id():
    id = deploy_market()
    logger.error(f"contract = {id}")
    print(f"contract = {id}")
    return id


@pytest.fixture(scope="session", autouse=True)
def mock_get_tezos_client_path():
    return os.path.join('tests/users', 'secret_keys')


@pytest.fixture(scope='function', autouse=True)
def mock_functions(monkeypatch):
    print("mock_function")
    monkeypatch.setattr(
        'src.utils.get_tezos_client_path',
        lambda: os.path.join('tests/users', 'secret_keys')
    )


@pytest.fixture(scope='session', autouse=True)
def stablecoin_id():
    id = deploy_stablecoin()
    logger.debug(f"stablecoin ID = {id}")
    return id


@pytest.fixture(scope="session", autouse=True)
def config(contract_id, stablecoin_id):
    config = Config(config_file="tests/cli.ini", contract=contract_id, stablecoin=stablecoin_id)
    logger.debug(f"endpoint = {config['endpoint']}")
    logger.debug(f"account originator = {config['admin_priv_key']}")
    return config


@pytest.fixture(scope="session", autouse=True)
def get_accounts(config):
    accounts = Accounts(endpoint=config["endpoint"])
    accounts.import_from_folder("tests/users")
    return accounts


@pytest.fixture(scope="session", autouse=True)
def revealed_accounts(financed_accounts, config):
    accounts_obj = Accounts(config["endpoint"])
    accounts_to_reveal = random.choices(financed_accounts, k=20)
    for account in financed_accounts:
        if account in accounts_to_reveal:
            accounts_obj.import_from_file(f"tests/users/{account['name']}.json", account['name'])
            accounts_obj.activate_account(account['name'])
            try:
                accounts_obj.reveal_account(account['name'])
                account["status"] += ",revealed"
            except:
                continue
    return accounts_to_reveal


@pytest.fixture(scope="session", autouse=True)
def accounts_who_minted(config, market, revealed_accounts, gen_cleared_markets):
    accounts_who_mint = random.choices(revealed_accounts, k=15)
    market_with_minted_token = random.choices(gen_cleared_markets, k=15)
    transactions = []
    for account in test_accounts:
        if account in accounts_who_mint:
            for ma in market_pool:
                if ma in market_with_minted_token:
                    try:
                        transaction = market.mint(ma['id'], account['name'], 2**16)
                        submit_transaction(transaction, error_func=print_error)
                        ma['status'] = 'minted'
                        if 'minted' not in account['status']:
                            account['status'] += 'minted'
                    except:
                        continue
    return accounts_who_mint


@pytest.fixture(scope="function")
def revealed_account(revealed_accounts, stablecoin, get_accounts):
    selected_account = random.choice(revealed_accounts)
    stablecoin_balance = stablecoin.get_balance(selected_account["name"])
    tez_balance = get_accounts[selected_account['name']].balance()
    logger.debug(f"acount use for the call: {selected_account}")
    logger.debug(f"account stablecoin balance before call: {stablecoin_balance}")
    logger.debug(f"account tez balance before call: {tez_balance}")
    yield selected_account
    logger.debug(f"account stablecoin balance after call: {stablecoin_balance}")
    logger.debug(f"account tez balance before call: {tez_balance}")


@pytest.fixture(scope="function")
def financed_account(financed_accounts, stablecoin, get_accounts):
    selected_account = random.choice(financed_accounts)
    stablecoin_balance = stablecoin.get_balance(selected_account["name"])
    tez_balance = get_accounts[selected_account['name']].balance()
    logger.debug(f"acount use for the call: {selected_account}")
    logger.debug(f"account stablecoin balance before call: {stablecoin_balance}")
    logger.debug(f"account tez balance before call: {tez_balance}")
    yield selected_account
    logger.debug(f"account stablecoin balance after call: {stablecoin_balance}")
    logger.debug(f"account tez balance before call: {tez_balance}")


@pytest.fixture(scope="function")
def non_financed_account(stablecoin, get_accounts):
    selection = [x for x in test_accounts if 'financed' not in x['status']]
    selected_account = random.choice(selection)
    stablecoin_balance = stablecoin.get_balance(selected_account["name"])
    tez_balance = get_accounts[selected_account['name']].balance()
    logger.debug(f"acount use for the call: {selected_account}")
    logger.debug(f"account stablecoin balance before call: {stablecoin_balance}")
    logger.debug(f"account tez balance before call: {tez_balance}")
    yield selected_account
    logger.debug(f"account stablecoin balance after call: {stablecoin_balance}")
    logger.debug(f"account tez balance before call: {tez_balance}")


@pytest.fixture(scope="function")
def minter_account():
    selection = [x for x in test_accounts if 'minted' in x['status']]
    account = random.choice(selection)
    return account


@pytest.fixture(scope="session", autouse="True")
def gen_markets(revealed_accounts, config, market, stablecoin_id):
    transactions = []
    for i in range(2):
        for index in range(40):
            quantity = random.randint(0, 900)
            rate = random.randint(0, 2 ** 63)
            end_delay = random.uniform(0.2, 0.5)
            end = datetime.now() + timedelta(minutes=end_delay)
            caller = random.choice(revealed_accounts)
            market_id, transaction = market.ask_question(
                id_generator(),
                id_generator(),
                caller['name'],
                quantity,
                rate,
                id_generator(),
                auction_end_date=end.timestamp(),
                token_contract=stablecoin_id
            )
            if market_id not in reserved and market_id != 1:
                reserved.append(market_id)
                transactions.append(transaction)
                market_pool.append({
                    'id': int(market_id),
                    'caller': caller,
                    'end': end.timestamp(),
                    'status': 'created'
                })
        bulk_transactions = config["admin_account"].bulk(*transactions)
        submit_transaction(bulk_transactions, error_func=print_error)
        sleep(2)
        transactions.clear()
    sleep(80)
    return market_pool


@pytest.fixture(scope="session", autouse="True")
def gen_bid_markets(gen_markets, market, config):
    selection = random.sample(gen_markets, k=60)
    for i in range(1):
        for ma in selection:
            transactions = market.multiple_bids(
                ma['id'],
                random.randint(2, 2 ** 8),
                random.randint(2, 2 ** 63)
            )
        bulk_transactions = config["admin_account"].bulk(transactions)
        submit_transaction(bulk_transactions, error_func=print_error)
        for ma in selection:
            ma['status'] = 'bidded'
        sleep(2)
    return selection


@pytest.fixture(scope="session", autouse="True")
def gen_cleared_markets(config, market, gen_bid_markets):
    selection = random.sample(gen_bid_markets, k=40)
    cleared = []
    for ma in selection:
        transaction = market.auction_clear(ma['id'], ma['caller']['name'])
        try:
            end = datetime.now()
            logger.debug(f" who is the end {end.timestamp()} {ma['end']}")
            submit_transaction(transaction, error_func=raise_error)
            ma['status'] = 'cleared'
            cleared.append(ma)
        except Exception as e:
            continue
    sleep(2)
    logger.debug(len(cleared))
    return cleared


@pytest.fixture(scope="session", autouse="True")
def gen_resolved_markets(config, market, gen_cleared_markets):
    selection = random.choices(gen_cleared_markets, k=20)
    resolved = []
    random_bit = random.getrandbits(1)
    random_boolean = bool(random_bit)
    for ma in market_pool:
        if ma in selection:
            transaction = market.close_market(ma['id'], ma['caller']['name'], random_boolean)
            try:
                submit_transaction(transaction, error_func=raise_error)
                ma['status'] = 'resolved'
                resolved.append(ma)
            except Exception as e:
                logger.debug(e)
                continue
    logger.debug(len(resolved))
    return resolved


@pytest.fixture(scope="function", autouse=True)
def log_contract_state(market):
    logger.debug("___________________")
    yield logger
    logger.debug("___________________")


def get_random_market(status='created'):
    pool = [x for x in market_pool if status == x['status']]
    logger.debug(pool)
    r_pool = random.choice(pool)
    pool.remove(r_pool)
    return r_pool


def pytest_configure():
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    # launch_sandbox()
    # sleep(20)


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
    # stop_sandbox()


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    start = time()
    yield
    total = time() - start
    logger.error(total)



def get_random_account(status="created", exclude=""):
    selection = [x for x in test_accounts if status not in x['status'] and status not in exclude]
    selected_account = random.choice(selection)
    stablecoin_balance = stablecoin.get_balance(selected_account["name"])
    tez_balance = get_accounts[selected_account['name']].balance()
    logger.debug(f"acount use for the call: {selected_account}")
    logger.debug(f"account stablecoin balance before call: {stablecoin_balance}")
    logger.debug(f"account tez balance before call: {tez_balance}")
    yield selected_account
    logger.debug(f"account stablecoin balance after call: {stablecoin_balance}")
    logger.debug(f"account tez balance before call: {tez_balance}")
    return selected_account


@pytest.fixture(scope="session", autouse=True)
def market(config, get_accounts):
    new_market = Market(get_accounts, config)
    return new_market


@pytest.fixture(scope="session", autouse=True)
def stablecoin(config, get_accounts):
    new_stablecoin = Stablecoin(get_accounts, config)
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
def financed_accounts(client, config: Config, stablecoin_id: str):
    money_seeding = []
    stablecoin_seeding = []
    accounts_to_finance = random.choices(test_accounts, k=30)
    for account in test_accounts:
        if account in accounts_to_finance:
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

    bulk_transactions = config["admin_account"].bulk(*stablecoin_seeding)
    submit_transaction(bulk_transactions, error_func=print_error)
    bulk_transactions = config["admin_account"].bulk(*money_seeding)
    submit_transaction(bulk_transactions, error_func=print_error)
    return accounts_to_finance


