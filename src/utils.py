import ast
import os
import random
import string
import sys

from loguru import logger

from pytezos import pytezos
from pytezos.rpc.node import RpcError

from src.errors import contract_error

logger = logger.opt(colors=True)

client = pytezos.using(
    shell="http://localhost:20000",
    key="edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq"
)


def get_public_key(account):
    """
    Get public key hash from account
    """
    return account.key.public_key_hash()


def get_stablecoin(account, stablecoin_contract: str):
    """
    Return an reference to the stablecoin contract for account
    """
    stablecoin_client = account.contract(stablecoin_contract)
    return stablecoin_client


def raise_error(_err_message):
    """
    Receive an error message and raise it
    """
    raise


def return_error(err_message):
    return err_message


def print_error(err_message):
    """
    Receive an error message and print it
    """
    if 'with' in err_message:
        if 'string' in err_message['with']:
            err_code = err_message['with']['string']
        elif 'int' in err_message['with']:
            err_code = err_message['with']['int']
        else:
            print(err_message)
            sys.exit()

        if err_code in contract_error:
            print("Error:", contract_error[err_code])
        else:
            print("Error:", err_code)
    else:
        print(err_message)


def print_and_ignore(err_message):
    """
    Receive and error message, print it and ignore it
    """
    if 'with' in err_message:
        err_code = err_message['with']['string']
        print(contract_error[err_code])
    else:
        print(err_message)
    sys.exit()


def submit_transaction(transaction, count=None, tries=3, error_func=None):
    """
    Submit a transaction
    """
    try:
        transaction_ = transaction.autofill(ttl=60, counter=count)
        res = transaction_.sign().inject(_async=False)
        if hasattr(sys, '_called_from_test'):
            client.bake_block().fill().work().sign().inject()
        else:
            client.bake_block().fill().work().sign().inject()
            #block_hash = transaction_.shell.wait_next_block(max_iterations=10)
            #logger.debug(f"block baked: {block_hash}")
        return res
    except RpcError as r:
        err_message = ast.literal_eval(str(r)[1:-2])
        if 'id' in err_message and tries >= 0:
            tries = tries - 1
            if 'counter_in_the_past' in err_message['id']:
                if 'expected' in err_message:
                    count = int(err_message['expected'])
                return submit_transaction(transaction, count=count, tries=tries, error_func=error_func)
            elif 'counter_in_the_future' in err_message['id']:
                if 'expected' in err_message:
                    count = int(err_message['expected'])
                return submit_transaction(transaction, count=count, tries=tries, error_func=error_func)
        logger.debug(f"the transaction couldn't be injected because of {err_message}")
        if error_func is not None:
            return error_func(err_message)
        raise


def get_tezos_client_path(client_path):
    """
    Obtain the tezos client path
    """
    logger.error(client_path)
    if not os.path.exists(client_path):
        os.makedirs(client_path)
    if not os.path.exists(client_path + '/secret_keys'):
        with open(client_path + '/secret_keys', 'x') as file:
            file.write('[]')
            logger.info('secret_keys file created')
    return os.path.expanduser(client_path)


def get_market_map(client, contract_id, market_id=None):
    """
    Return storage for questions
    """
    contract = client.contract(contract_id)
    if market_id is None:
        return contract.storage['business_storage']['markets']['market_map']
    return contract.storage['business_storage']['markets']['market_map'][market_id]()


def get_tokens_ledgermap(client, contract_id):
    """
    Return storage for tokens
    """
    contract = client.contract(contract_id)
    return contract.storage['business_storage']['tokens']['ledger_map']


def get_tokens_supplymap(client, contract_id):
    """
    Return storage for tokens
    """
    contract = client.contract(contract_id)
    return contract.storage['business_storage']['tokens']['supply_map']


def get_question_liquidity_provider_map(client, contract_id, market_id=None, address=None):
    """
    Return storage for liquidity provider
    """
    contract = client.contract(contract_id)
    if market_id is None or address is None:
        return contract.storage['business_storage']['markets']['liquidity_provider_map']
    key = {'originator': address, 'market_id': market_id}
    return contract.storage['business_storage']['markets']['liquidity_provider_map'][key]()


def stablecoin_storage(client, contract_id, market_id=None):
    """
    Return storage for stablecoin
    """
    stablecoin = get_stablecoin(client, contract_id)
    if market_id is None:
        return stablecoin.storage['ledger']
    return stablecoin.storage['ledger'][market_id]


def get_tokens_id_list(market_id: int):
    token_list = [
        {'token_name': 'no_token', 'token_value': market_id << 3},
        {'token_name': 'yes_token', 'token_value': (market_id << 3) + 1},
        {'token_name': 'pool_liquidity', 'token_value': (market_id << 3) + 2},
        {'token_name': 'auction_reward', 'token_value': (market_id << 3) + 3},
        {'token_name': 'liquidity_reward', 'token_value': (market_id << 3) + 4},
    ]
    return token_list


def id_generator(size=17, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def log_and_submit(transaction, account, market=None, market_id=None, error_func=raise_error, logging=True):
    payload_parameters = transaction.json_payload()['contents'][0]['parameters']
    entrypoint = payload_parameters['entrypoint']
    params = payload_parameters['value']
    logger.debug(f"{market_id} {account['key']} {entrypoint} {params}")
    before_storage, after_storage = None, None
    if market is not None and logging is True:
        try:
            before_storage = market.get_storage(market_id, account['name'])
            logger.debug(f"{before_storage}")
        except Exception as e:
            logger.debug(f"storage is not accessible before submit transaction: {e}")
    result = submit_transaction(transaction, error_func=error_func)
    logger.debug(f"Result from TRANSACTION = {result}")
    if market is not None and logging is True:
        try:
            after_storage = market.get_storage(market_id, account['name'])
            logger.debug(f"{after_storage}")
        except Exception as e:
            logger.debug(f"storage is not accessible after submit transaction: {e}")
    return before_storage, after_storage
