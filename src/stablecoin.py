from src.accounts import Accounts
from src.config import Config

class Stablecoin:
    """
    Stablecoin Class
    """
    def __init__(
            self,
            accounts: Accounts,
            config: Config,
            contract_id
    ):
        self.accounts = accounts
        self.config = config
        self.contract = contract_id

    def pm_contracts(
        self,
        user: str
    ):
        return self.accounts[user].contract(self.contract)

