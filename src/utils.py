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


def get_stablecoin(account, contract: str):
    """
    Return an reference to the stablecoin storage  for account
    """
    stablecoin_contract = account.contract(contract).storage["stablecoin"]()
    stablecoin_client = account.contract(stablecoin_contract)
    return stablecoin_client


def raise_error(_err_message):
    raise


def print_error(err_message):
    if 'with' in err_message:
        err_code = err_message['with']['string']
        print(contract_error[err_code])
    else:
        print(err_message)
    sys.exit()


def print_and_ignore(err_message):
    if 'with' in err_message:
        err_code = err_message['with']['string']
        print(contract_error[err_code])
    else:
        print(err_message)
    sys.exit()


def submit_transaction(transaction, count=None, tries=0, error_func=None):
    try:
        source = transaction.key.public_key_hash()
        contract_count = transaction.shell.contracts[source].count()
        if count is not None and count < contract_count:
            count = contract_count
        transaction = transaction.autofill(counter=count, branch_offset=1).sign()
        transaction.inject()
    except RpcError as r:
        err_message = ast.literal_eval(str(r)[1:-2])
        if err_message['id'] == 'proto.alpha.contract.counter_in_the_past' and tries > 0:
            submit_transaction(transaction, count=count + 1, tries=tries - 1, error_func=error_func)
            return
        elif err_message['id'] == 'proto.alpha.contract.counter_in_the_future':
            submit_transaction(transaction, count=count - 1, tries=tries - 1, error_func=error_func)
        if error_func is not None:
            error_func(err_message)


def get_tezos_client_path():
    """
    Obtain a tezos path
    """
    return os.path.expanduser(
        os.path.join('~/.tezos-client', 'secret_keys')
    )
