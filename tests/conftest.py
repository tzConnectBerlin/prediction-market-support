# content of conftest.py
import os
import random
import sys

from time import sleep, time
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
import requests.exceptions

from testcontainers.core.generic import DockerContainer
from loguru import logger
from pytezos import pytezos
from pytezos import Undefined
from pytezos.michelson.forge  import optimize_timestamp
from unittest.mock import patch, MagicMock

from src.accounts import Accounts
from src.config import Config
from src.compile import launch_sandbox, stop_sandbox
from src.deploy import deploy_market, deploy_stablecoin
from src.market import Market
from src.stablecoin import Stablecoin
from src.utils import *


market_pool = []
reserved = []

logger.add("tests/file_{time}.log", level='DEBUG')
logger = logger.opt(colors=True)


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
    {"name": "leonidas", "key": "tz1ZrWi7V8tu3tVepAQVAEt8jgLz4VVEEf7m", "status": "created"}
]

funded_accounts = test_accounts[0:25]
revealed_accounts = test_accounts[0:30]
tezzed_accounts = test_accounts[0:30]

header_timestamp = None

clientInstance = None

USDtzLeger = {
        'storage': {
            'totalSupply': 0,
            'ledger': {
                'tz1gjaF81ZRRvdzjobyfVNsAeSC6PScjfQwN': {
                    'balance': 2**65,
                    'allowances': {}
                }
            }
        }
}


binary_contract = {
    'storage': {
        'lambda_repository':
            {
                'creator': 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb',
                'lambda_map': {}
            },
        'business_storage': {
            'tokens': {'ledger_map': {}, 'supply_map': {}},
            'markets': {'market_map': {}, 'liquidity_provider_map': {}}}
    }
}


@pytest.fixture(scope="session", autouse=True)
def endpoint():
    return 'http://localhost:20001'


@pytest.fixture(scope="session", autouse=True)
def client(endpoint):
    client = pytezos.using(
        shell=endpoint
    ).using(
        key='edpkvGfYw3LyB1UcCahKQk4rF2tvbMUk8GFiTuMjL75uGXrpvKXhjn'
    )
    clientInstance = client
    return client


@pytest.fixture(scope="function", autouse=True)
def header_timestamp(client):
    header_time = client.shell.blocks['head'].header.shell()['timestamp']
    header_timestamp = optimize_timestamp(header_time)
    return header_timestamp


@pytest.fixture(scope="session", autouse=True)
def contract_id(endpoint, stablecoin_id):
    id = deploy_market(shell=endpoint)
    '''
    if os.path.exists('data.json'):
        with open('data.json', "r") as outfile:
            data = eval(outfile.read())
            logger.info(data['business_storage'])
            logger.info(binary_contract['storage']['business_storage'])
            binary_contract['storage']['business_storage'] = data['business_storage']
    logger.info('aaaaaaFILe')
    logger.info(binary_contract['storage']['business_storage'])
    for key, _value in binary_contract['storage']['business_storage']['markets']['market_map']:
        logger.info(f"{key} {_value}")
        binary_contract['storage']['business_storage']['markets']['market_map'][key]['metadata']['fa12'] = stablecoin_id
    '''
    logger.info(f"Binary prediction contract deployed at address {id}")
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
def stablecoin_id(endpoint):
    USDtzLeger['storage']['ledger']['tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb'] = {'balance': 2**65, 'allowances': {}}
    #put tezos in
    for account in test_accounts[0:25]:
        logger.info(account)
        USDtzLeger['storage']['ledger'][account['key']] = {'balance': 2**65, 'allowances': {}}
    id = deploy_stablecoin(shell=endpoint, storage=USDtzLeger)
    logger.info(f"Stablecoin contract deployed at  = {id}")
    return id


@pytest.fixture(scope="session", autouse=True)
def stablecoin(config, accounts_instance):
    new_stablecoin = Stablecoin(accounts_instance, config)
    return new_stablecoin


@pytest.fixture(scope="session", autouse=True)
def config(contract_id, stablecoin_id, endpoint):
    config = Config(
        config_file="tests/cli.ini",
        contract=contract_id,
        endpoint=endpoint,
        ipfs_server="",
        stablecoin=stablecoin_id
    )
    logger.info(f"account originator = {config['admin_priv_key']}")
    logger.info(f"account originator = {config.data}")
    logger.info(f"account originator = {config.get_admin_account()}")
    return config


@pytest.fixture(scope="session", autouse=True)
def accounts_instance(endpoint):
    accounts = Accounts(endpoint)
    users = ['siri', 'leonidas', 'rimk', 'donald', 'mala', 'stavros', 'marty']
    for user in users:
        accounts.import_from_file(f'tests/users/{user}.json', user)
    return accounts


@pytest.fixture(scope="session", autouse=True)
def market(config, accounts_instance):
    new_market = Market(accounts_instance, config)
    return new_market


def get_market(caller):
    end = datetime.now() + timedelta(seconds=random.uniform(0.15, 2.5))

    market_id, transaction = market.ask_question(
        id_generator(),
        id_generator(),
        caller['name'],
        1000,
        2 ** 63,
        id_generator(),
        auction_end_date=end.timestamp(),
        token_contract=stablecoin_id
    )
    log_and_submit(transaction, caller, market, market_id, error_func=raise_error, logging=False)

    return market_id


def get_cleared_market(caller):
    auction_end = clientInstance.shell.blocks['head'].header.shell()['timestamp']
    end_timestamp = optimize_timestamp(auction_end)
    market_id, transaction = market.ask_question(
        "when",
        "tomorrow",
        caller["name"],
        1000,
        2 ** 63,
        caller['key'],
        auction_end_date=end_timestamp,
        market_id=None,
        token_contract=None
    )
    log_and_submit(transaction, caller, market, market_id, logging=True)

    transaction = market.auction_clear(market_id, caller["name"])
    log_and_submit(transaction, caller, market, market_id, logging=True)

    return market_id

'''
@pytest.fixture(scope="session", autouse="True")
def gen_markets(revealed_accounts, config, market, stablecoin_id, accounts_instance):
    transactions = []
    count = 0
    while count < 1:
        quantity = random.randint(1, 900)
        rate = random.randint(1, 2 ** 63)
        end_delay = random.uniform(0.001, 0.002)
        end = datetime.now() + timedelta(minutes=end_delay)
        caller = random.choice(revealed_accounts)
        try:
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
            submit_transaction(transaction)
            if market_id not in reserved and market_id != 1:
                reserved.append(market_id)
                transactions.append(transaction)
                market_pool.append({
                    'id': int(market_id),
                    'caller': caller,
                    'end': end.timestamp(),
                    'status': 'created'
                })
                count += 1
        except Exception as e:
            logger.error(e)
            continue
    assert len(market_pool) > 0
    accounts = accounts_instance
    print_full_storage(market_pool, market, accounts)
    return market_pool


@pytest.fixture(scope="session", autouse="True")
def gen_bid_markets(gen_markets, market, config, accounts_instance):
    selection = random.sample(gen_markets, k=50)
    bidded = []
    for i in range(1):
        for ma in selection:
            try:
                transactions = market.multiple_bids(
                    ma['id'],
                    random.randint(2, 2 ** 8),
                    random.randint(2, 2 ** 63)
                )
                submit_transaction(transactions, error_func=print_error)
                ma['status'] = 'bidded'
                bidded.append(ma)
            except:
                continue
    assert len(selection) > 0
    logger.info('#####################BIDDED MARKETS##########################')
    logger.info(selection)
    logger.info(len(selection))
    accounts = accounts_instance
    #print_full_storage(bidded, market, accounts)
    logger.info('########################BIDDED#####################################')
    return bidded


@pytest.fixture(scope="session", autouse="True")
def gen_cleared_markets(config, market, gen_bid_markets, revealed_accounts, accounts_instance):
    selection = random.sample(gen_bid_markets, k=35)
    cleared = []
    for ma in selection:
        transaction = market.auction_clear(ma['id'], ma['caller']['name'])
        try:
            end = datetime.now()
            submit_transaction(transaction, error_func=raise_error)
            ma['status'] = 'cleared'
            cleared.append(ma)
        except Exception as e:
            continue
    logger.info('#####################CLEARED MARKETS##########################')
    logger.info(selection)
    logger.info(len(selection))
    accounts = accounts_instance
    #print_full_storage(cleared, market, accounts)
    logger.info('########################CLEARED#####################################')
    assert len(cleared) > 0
    return cleared

'''


def print_full_storage(cleared, accounts):
    market_map = {}
    liquidity_provider_map = {}
    supply_map = {}
    ledger_map = {}
    for ma in cleared:
        storage = market.get_storage(ma['id'], debug=False)
        market_map[ma['id']] = storage['market_map']
        supply_map |= storage['supply_map']
        ledger_map |= storage['ledger_map']
        liquidity_provider_map |= storage['liquidity_provider_map']
    full_storage = {
        'business_storage': {
        'tokens': {
            'supply_map': supply_map,
            'ledger_map': ledger_map
        },
        'markets': {
            'market_map': market_map,
            'liquidity_provider_map': liquidity_provider_map
        }
         }
    }
    logger.info(full_storage)
    file_name = 'data.json'
    with open(file_name, "w+") as outfile:
        outfile.write(str(full_storage))

'''
@pytest.fixture(scope="session", autouse="True")
def gen_resolved_markets(config, market, gen_cleared_markets, accounts_instance):
    selection = random.choices(gen_cleared_markets, k=25)
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
                logger.info(e)
                continue
    assert len(selection) > 0
    logger.info('#####################RESOLVED MARKETS##########################')
    logger.info(selection)
    logger.info(len(selection))
    #print_full_storage(resolved, market, accounts)
    logger.info(market_pool)
    accounts = accounts_instance
    print_full_storage(market_pool, market, accounts)
    logger.info('########################RESOLVED##################################')
    return resolved
'''
'''

'''
@pytest.fixture(scope="function", autouse=True)
def log_contract_state(request):
    logger.info(f"-----------------------------{request}-----------------------------")
    yield
    logger.info(f"-----------------------------END OF THE TEST-----------------------------")


def pytest_configure():
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    sys._called_from_test = True
    launch_sandbox()
    sleep(5)


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """


def pytest_unconfigure(config):
    """
    Called before test process is exited.
    """
    del sys._called_from_test
    stop_sandbox()