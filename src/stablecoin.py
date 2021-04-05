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
            contract_id
    ):
        self.accounts = accounts
        self.config = config
        self.contract = contract_id
        self.client = config['admin_account'].contract(config['stablecoin'])

    def approve(self, spender: str, value: int):
        spender_address = get_public_key(self.accounts[spender])
        operation = self.client.approve(
           spender_address,
           value
        )
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def burn(self, dest: str, value: int):
        dest_address = get_public_key(self.accounts[dest])
        operation = self.client.burn({
            'from': dest_address,
            'value': value
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def get_allowance(self, spender: str):
        """
        Check how much can be spend
        """
        spender_address = get_public_key(self.accounts[spender])
        owner_address = self.client.key.public_key_hash()
        operation = self.client.getAllowance({
            'owner': owner_address,
            'spender': spender_address,
            'contract': self.contract
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def mint(self, to: str, value: int):
        """
        Mint stablecoin for account to
        """
        to_address = get_public_key(self.accounts[to])
        operation = self.client.mint({
            'to': to_address,
            'value': value
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def transfer(self, src: str, dest: str, value: int):
        """
        Transfer stablecoin between two adresses
        """
        src_address = get_public_key(self.accounts[src])
        dest_address = get_public_key(self.accounts[dest])
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
        dest_address = get_public_key(self.accounts[dest])
        operation = self.client.transfer({
            'from': src_address,
            'to': dest_address,
            'value': value
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)