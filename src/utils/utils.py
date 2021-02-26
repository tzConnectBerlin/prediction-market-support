from pytezos import pytezos

def get_stablecoin(account, contract: str):
    """
    Return an reference to the stablecoin storage  for account
    """
    stablecoin_contract = account.contract(contract)\
            .storage["stablecoin"]()
    stablecoin_client = account.contract(stablecoin_contract)
    return stablecoin_client

def get_public_key(account):
    """
    Get public key hash from account
    """
    return account.key.public_key_hash()

def get_count(contract, account):
    """
    Get count from contract
    """
    return contract.shell.head.context \
            .contracts[account].count()

