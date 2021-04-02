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
        self.client = Config['admin-account'].contract(contract_id)

    def pm_contracts(
        self,
        user: str
    ):
        return self.accounts[user].contract(self.contract)

    def approve(self, spender: str, value: int):
        operation = self.client.approve({
            'spender': str,
            'value': int
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def burn(self, dest: str, value: int):
        operation = self.client.burn({
            'from': dest,
            'value': value
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def get_allowance(self, owner: str, spender: str, contract: str):
        operation = self.client.getAllowance({
            'owner': str,
            'spender': str,
            'contract': str
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def mint(self, to: str, value: int):
        operation = self.client.mint({
            'to': to,
            'value': value
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def transfer(self, src: str, dest: str, value: int):
        operation = self.client.transfer({
            'from': get_public_key(self.config["admin_account"]),
            'to': get_public_key(self.accounts[dest]),
            'value': value
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)
