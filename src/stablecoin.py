from pytezos import Undefined

from src.accounts import Accounts
from src.config import Config
from src.utils import get_public_key, submit_transaction, print_error


class Stablecoin:
    """
    Stablecoin Class
    """
    def __init__(
            self,
            accounts: Accounts,
            config: Config,
    ):
        self.accounts = accounts
        self.config = config
        self.market_id = config['contract']
        self.client = config['admin_account'].contract(config['stablecoin'])


    def pm_contracts(
            self,
            user: str
    ):
        return self.accounts[user].contract(self.config['stablecoin'])

    def approve_market(self, owner: str, value: int):
        """
        Approve usage of tokens by market for owner
        """
        operation = self.pm_contracts(owner).approve(
           self.market_id,
           value
        )
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def burn(self, dest: str, value: int):
        dest_address = self.accounts[dest].key.public_key_hash()
        operation = self.client.burn({
            'from': dest_address,
            'value': value
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    #Not working, check with shubendu
    def get_allowance(self, owner: str):
        """
        Check how much can be spent
        """
        owner_address = self.accounts[owner].key.public_key_hash()
        operation = self.client.getAllowance({
            'owner': owner_address,
            'spender': self.market_id,
            'contract_2': self.market_id
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def mint(self, to: str, value: int):
        """
        Mint stablecoin for account to
        """
        to_address = self.accounts[to].key.public_key_hash()
        operation = self.client.mint({
            'to': to_address,
            'value': value
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def transfer(self, src: str, dest: str, value: int):
        """
        Transfer stablecoin between two adresses
        """
        src_address = self.accounts[src].key.public_key_hash()
        dest_address = self.accounts[dest].key.public_key_hash()
        operation = self.client.transfer({
            'from': src_address,
            'to': dest_address,
            'value': value
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def fund(self, dest: str, value: int):
        """
        Fund a account with stablecoin
        """
        src_address = self.client.key.public_key_hash()
        dest_address = self.accounts[dest].key.public_key_hash()
        operation = self.client.transfer({
            'from': src_address,
            'to': dest_address,
            'value': value
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)