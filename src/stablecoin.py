from loguru import logger
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
        self.client = None
        self.config = config
        self.market_id = config['contract']
        self._clients = {}
    
    def get_client(self):
        if self.client is None:
            try: 
                self.client = self.config['admin_account'].contract(
                    self.config['stablecoin']
                )
            except Exception as e:
                logger.debug(e)
                logger.debug(
                    f'Stablecoin contract {self.config["stablecoin"]} was not found on {self.config["endpoint"]}'
                )
                raise
        return self.client

    def pm_contracts(
            self,
            user: str
    ):
        if user not in self._clients:
            self._clients[user] = self.accounts[user].contract(self.contract)
        return self._clients[user]

    def approve_market(self, owner: str, value: int):
        """
        Approve usage of tokens by market for owner
        """
        operation = self.pm_contracts(owner).approve(
           self.market_id,
           value
        )
        return operation.as_transaction()

    def get_allowance(self, owner: str):
        """
        Check how much can be spent
        """
        owner_address = self.accounts[owner].key.public_key_hash()
        operation = self.get_client().getAllowance({
            'owner': owner_address,
            'spender': self.market_id,
            'contract_2': self.market_id
        })
        return operation.as_transaction()

    def transfer(self, src: str, dest: str, value: int):
        """
        Transfer stablecoin between two adresses
        """
        src_address = self.accounts[src].key.public_key_hash()
        dest_address = self.accounts[dest].key.public_key_hash()
        operation = self.get_client().transfer({
            'from': src_address,
            'to': dest_address,
            'value': value
        })
        return operation.as_transaction()

    def fund(self, dest: str, value: int):
        """
        Fund a account with stablecoin
        """
        dest_address = self.accounts[dest].key.public_key_hash()
        operation = self.get_client().transfer({
            'from': get_public_key(self.config["admin_account"]),
            'to': dest_address,
            'value': value
        })
        return operation.as_transaction()

    def get_balance(self, user: str):
        user_address = self.accounts[user].key.public_key_hash()
        balance = self.get_client().getBalance(
            {'owner': user_address, 'contract_1': Undefined}
        ).callback_view()
        return int(balance)
