import os
import subprocess

import glob
from pytezos import pytezos, Key

from src.utils.utils import submit_transaction

class Accounts:
    """
    User Class for Handling tezos accounts
    """

    def __init__(self, endpoint, folder="users"):
        self.accounts = {}
        self.endpoint = endpoint
        if folder != None:
            self.import_from_folder(folder)

    def __getitem__(self, account_name: str):
        if account_name in self.accounts:
            return self.accounts[account_name]

    def __contains__(self, key):
        return key in self.accounts 
        
    def names(self):
        return list(self.accounts.keys())
    
    def import_from_folder(self, accounts_folder):
        """
        Get all the account data from the account folder account
        """
        account_list = glob.glob(f"{accounts_folder}/*.json")
        for account_file in account_list:
            file_name = os.path.basename(account_file)
            name = os.path.splitext(file_name)[0]
            self.import_from_file(account_file, name)

    def import_from_file(self, account_data: str, account_name: str):
        account = pytezos.using(
            key = account_data,
            shell = self.endpoint,
        )
        if account_name in self.accounts:
            print(f"user {account_name} as aready been imported, reimporting it")
        self.accounts[account_name] = account

    def import_from_tezos_client(self, account_name: str):
        """
        Import account from tezos client
        """
        key = Key.from_alias(account_name)
        self.import_from_file(key.public_key_hash(), account_name)
        

    def import_to_tezos_client(self, account_name: str):
        """
        Import_account to tezos client
        """
        env = dict(os.environ)
        host = self.endpoint
        subprocess.run(
            [
                'tezos-client',
                '-E',
                host,
                'import',
                'secret',
                'key',
                account_name,
                f"unencrypted:{self.accounts[account_name].key.secret_key()}",
                '--force'
            ],
            env=env,
            check=False,
        )

    def activate_account(self, account_name: str):
        """
        Activate account
        """
        if self.accounts[account_name].balance() == 0:
            operation = self.accounts[account_name].activate_account()
            submit_transaction(operation)


    def reveal_account(self, account_name: str):
        """
        Reveal account
        """
        operation = self.accounts[account_name].reveal()
        submit_transaction(operation)

    def get_account(self, account_name: str):
        """
        Return account for account
        """
        return self.accounts[account_name]

    def contract_accounts(self, contract: str):
        contract_clients = {}
        for account_name in self.accounts:
            contract_clients[account_name] = self.accounts[account_name].contract(contract)
        return contract_clients
