import utils.summary


def get_stablecoin(account):
    """
    Return an reference to the stablecoin storage  for account
    """
    stablecoin = account.contract(
        summary.get_storage(config['Tezos']['pm_contract'])['stablecoin']
    )
    return stablecoin

def get_public_key(account):
    """
    Get public key hash from account
    """
    return account.key.public_key_hash()
