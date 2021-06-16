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
from unittest.mock import patch, MagicMock

from src.accounts import Accounts
from src.config import Config
from src.compile import launch_sandbox, stop_sandbox
from src.deploy import deploy_market, deploy_stablecoin
from src.market import Market
from src.stablecoin import Stablecoin
from src.utils import *


import ujson
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
    {"name": "stavros", "key": "tz1iPFr4obPeSzknBPud8uWXZC7j5gKoah8d", "status": "created"},
    {"name": "leonidas", "key": "tz1ZrWi7V8tu3tVepAQVAEt8jgLz4VVEEf7m", "status": "created"}
]

funded_accounts = test_accounts[0::25]
revealed_accounts = test_accounts[0::30]
tezzed_accounts = test_accounts[0::30]

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


for account in funded_accounts:
    pkh = account['key']
    storage = USDtzLeger['storage']['ledger'][pkh] = {'balance': 2**65, 'allowances': {}}


@pytest.fixture(scope="session", autouse=True)
def endpoint():
    return 'http://localhost:20000'


@pytest.fixture(scope="session")
def activate_protocol(endpoint):
    pytezos.using(
        shell=endpoint
    ).using(
        key='dictator'
    ).activate_protocol(
        "PsFLorenaUUuikDWvMDr6fGBRG8kt3e3D3fHoXK1j1BFRxeSH4i" #Florence
    ).fill(block_id='genesis').sign().inject()


@pytest.fixture(scope="session", autouse=True)
def client(endpoint):
    client = pytezos.using(
        shell=endpoint
    ).using(
        key='edpkvGfYw3LyB1UcCahKQk4rF2tvbMUk8GFiTuMjL75uGXrpvKXhjn'
    )
    return client


def submit_transaction_fixture(client):
    logger.info("Patching submit transaction")
    with patch(
        'src.utils.submit_transaction',
        autospec=True,
    ) as mock_submit:
        logger.info(mock_submit.call_args)
        args, kwargs = mock_submit.call_args
        submit_transaction(*args, **kwargs)
        client.bake_block().fill().work().sign().inject()
        yield
    logger.info("patchin complete unpatching")


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
    id = deploy_stablecoin(shell=endpoint, storage=USDtzLeger)
    logger.info(f"Stablecoin contract deployed at  = {id}")
    return id


@pytest.fixture(scope="session", autouse=True)
def stablecoin(config, get_accounts):
    new_stablecoin = Stablecoin(get_accounts, config)
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
def get_accounts(endpoint):
    accounts = Accounts(endpoint)
    accounts.import_from_folder("tests/users")
    return accounts


@pytest.fixture(scope="session", autouse=True)
def market(config, get_accounts):
    new_market = Market(get_accounts, config)
    return new_market


@pytest.fixture(scope="session", autouse=True)
def financed_accounts(client, config: Config, stablecoin_id: str):
    money_seeding = []
    stablecoin_seeding = []
    for i in range(25):
        account = test_accounts[i]
        if True:
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
    submit_transaction(bulk_transactions, error_func=raise_error)
    sleep(3)
    bulk_transactions = config["admin_account"].bulk(*money_seeding)
    submit_transaction(bulk_transactions, error_func=raise_error)
    return funded_accounts


@pytest.fixture(scope="session", autouse=True)
def revealed_accounts(financed_accounts, config, get_accounts):
    accounts_obj = get_accounts
    accounts_to_reveal = random.choices(financed_accounts, k=30)
    for i in range(30):
        account = test_accounts[i]
        if account in accounts_to_reveal:
            accounts_obj.activate_account(account['name'])
            try:
                accounts_obj.reveal_account(account['name'])
                account["status"] += ",revealed"
            except:
                continue
    return accounts_to_reveal


@pytest.fixture(scope="function")
def revealed_account(revealed_accounts, stablecoin, get_accounts):
    selected_account = random.choice(revealed_accounts)
    stablecoin_balance = stablecoin.get_balance(selected_account["name"])
    tez_balance = get_accounts[selected_account['name']].balance()
    logger.info(f"acount use for the call: {selected_account}")
    logger.info(f"account stablecoin balance before call: {stablecoin_balance}")
    logger.info(f"account tez balance before call: {tez_balance}")
    yield selected_account
    logger.info(f"account stablecoin balance after call: {stablecoin_balance}")
    logger.info(f"account tez balance before call: {tez_balance}")


@pytest.fixture(scope="function")
def financed_account(financed_accounts, stablecoin, get_accounts):
    selected_account = random.choice(financed_accounts)
    stablecoin_balance = stablecoin.get_balance(selected_account["name"])
    tez_balance = get_accounts[selected_account['name']].balance()
    logger.info(f"acount use for the call: {selected_account}")
    logger.info(f"account stablecoin balance before call: {stablecoin_balance}")
    logger.info(f"account tez balance before call: {tez_balance}")
    yield selected_account
    logger.info(f"account stablecoin balance after call: {stablecoin_balance}")
    logger.info(f"account tez balance before call: {tez_balance}")


@pytest.fixture(scope="function")
def non_financed_account(client, stablecoin, get_accounts):
    selection = [x for x in test_accounts if 'financed' not in x['status']]
    selected_account = random.choice(selection)
    stablecoin_balance = stablecoin.get_balance(selected_account["name"])
    tez_balance = get_accounts[selected_account['name']].balance()
    logger.info(f"acount used for the call: {selected_account}")
    transaction = client.transaction(
        selected_account['key'], amount=Decimal(10)
    )
    submit_transaction(transaction, error_func=raise_error)
    logger.info(f"{selected_account['key']} as money")
    try:
        get_accounts.activate_account(account_name=selected_account['name'])
        get_accounts.reveal_account(account_name=selected_account['name'])
    except:
        logger.info(f"Non financed account: {selected_account} already available on the network")
    logger.info(f"account stablecoin balance before call: {stablecoin_balance}")
    logger.info(f"account tez balance before call: {tez_balance}")
    yield selected_account
    logger.info(f"account stablecoin balance after call: {stablecoin_balance}")
    logger.info(f"account tez balance before call: {tez_balance}")


@pytest.fixture(scope="function")
def minter_account(accounts_who_minted):
    selection = [x for x in test_accounts if 'minted' in x['status']]
    account = random.choice(selection)
    return account


'''
@pytest.fixture(scope="session", autouse="True")
def gen_markets(revealed_accounts, config, market, stablecoin_id, get_accounts):
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
    accounts = get_accounts
    print_full_storage(market_pool, market, accounts)
    return market_pool


@pytest.fixture(scope="session", autouse="True")
def gen_bid_markets(gen_markets, market, config, get_accounts):
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
    accounts = get_accounts
    #print_full_storage(bidded, market, accounts)
    logger.info('########################BIDDED#####################################')
    return bidded


@pytest.fixture(scope="session", autouse="True")
def gen_cleared_markets(config, market, gen_bid_markets, revealed_accounts, get_accounts):
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
    accounts = get_accounts
    #print_full_storage(cleared, market, accounts)
    logger.info('########################CLEARED#####################################')
    assert len(cleared) > 0
    return cleared

'''


def print_full_storage(cleared, market, accounts):
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
def gen_resolved_markets(config, market, gen_cleared_markets, get_accounts):
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
    accounts = get_accounts
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
    #container = DockerContainer(
    #    'bakingbad/sandboxed-node:v9.0-rc1-1',
    #)
    #container.ports[8732] = 20000
    #container.with_name('flextesa-sandbox')
    #sys._container = container
    #sys._container.start()
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
    #sys._container.stop()
    del sys._called_from_test
    #stop_sandbox()


#@pytest.hookimpl(hookwrapper=True)
#def pytest_fixture_setup(fixturedef, request):

def get_random_account(status="created", exclude=""):
    selection = [x for x in test_accounts if status not in x['status'] and status not in exclude]
    selected_account = random.choice(selection)
    stablecoin_balance = stablecoin.get_balance(selected_account["name"])
    tez_balance = get_accounts[selected_account['name']].balance()
    logger.info(f"acount use for the call: {selected_account}")
    logger.info(f"account stablecoin balance before call: {stablecoin_balance}")
    logger.info(f"account tez balance before call: {tez_balance}")
    yield selected_account
    logger.info(f"account stablecoin balance after call: {stablecoin_balance}")
    logger.info(f"account tez balance before call: {tez_balance}")
    return selected_account

def get_random_market(status=['created'], exclude=[]):
    pool = [
        x for x in market_pool if x['status'] in status
    ]
    r_pool = random.choice(pool)
    logger.info(f"selected market for test: {r_pool}")
    return r_pool

