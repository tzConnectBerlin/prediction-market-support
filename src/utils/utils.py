import ast
import json

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

def submit_transaction(transaction, account, count=None, tries=None, error_func=None):
    try:
        transaction = transaction.autofill(counter=count,branch_offset=1).sign()
        transaction.inject()
    except Exception as e:
        error_message = ast.literal_eval(str(e)[1:-2])
        splited_error_message = error_message["id"].split('.')
        if error_func != None:
            error_func(error_message)
        print(splited_error_message[3])
        print(e)
        #raise
