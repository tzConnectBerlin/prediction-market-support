from utils import summary


def get_stablecoin(account, contract):
    """
    Return an reference to the stablecoin storage  for account
    """
    stablecoin = account.contract(
        summary.get_storage(contract)['stablecoin']
    )
    return stablecoin

def get_public_key(account):
    """
    Get public key hash from account
    """
    return account.key.public_key_hash()
