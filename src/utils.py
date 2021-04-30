import ast
import os
import sys

from pytezos.rpc.node import RpcError

from src.errors import contract_error

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
    sys.exit()


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
        source = transaction.key.public_key_hash()
        transaction_ = transaction.autofill(ttl=56)
        res = transaction_.sign().inject()
        transaction_.shell.wait_next_block()
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
        if error_func is not None:
            error_func(err_message)


def get_tezos_client_path():
    """
    Obtain the tezos client path
    """
    return os.path.expanduser('~/.tezos-client')


def get_market_map(client, contract_id):
    """
    Return storage for questions
    """
    contract = client.contract(contract_id)
    return contract.storage['business_storage']['markets']['market_map']


def get_question_liquidity_provider_map(client, contract_id):
    """
    Return storage for liquidity provider
    """
    contract = client.contract(contract_id)
    return contract.storage['business_storage']['markets']['liquidity_provider_map']


def stablecoin_storage(client, contract_id):
    """
    Return storage for stablecoin
    """
    stablecoin = get_stablecoin(client, contract_id)
    return stablecoin.storage['ledger']