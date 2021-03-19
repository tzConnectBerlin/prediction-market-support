import ast
import json
import os

from pytezos import pytezos

def get_public_key(account):
    """
    Get public key hash from account
    """
    return account.key.public_key_hash()

def get_stablecoin(account, contract: str):
    """
    Return an reference to the stablecoin storage  for account
    """
    stablecoin_contract = account.contract(contract)\
            .storage["stablecoin"]()
    stablecoin_client = account.contract(stablecoin_contract)
    return stablecoin_client

def raise_error(error_message):
    raise

def submit_transaction(transaction, count=None, tries=None, error_func=None):
    try:
        transaction = transaction.autofill(counter=count,branch_offset=1).sign()
        transaction.inject()
    except Exception as e:
        error_message = ast.literal_eval(str(e)[1:-2])
        splited_error_message = error_message["id"].split('.')
        if error_func != None:
            error_func(splited_error_message)
        print(e)
        
def get_tezos_client_path():
    """
    Obtain a tezos path
    """
    return os.path.expanduser(
        os.path.join('~/.tezos-client', 'secret_keys')
    )
