import os
import subprocess

import glob
from pytezos import pytezos

class Accounts:
    """
    User Class for Handling tezos accounts
    """

    def __init__(self, folder="users", endpoint="http://localhost:2000"):
        self.accounts = {}
        self.endpoint = endpoint
        print("folder", folder)
        if folder != None:
            self.import_from_folder(folder)

    def import_from_folder(self, accounts_folder):
        """
        Get all the account data from the account folder account
        """
        account_list = glob.glob(f"{accounts_folder}/*.json")
        for account_file in account_list:
            file_name = os.path.basename(account_file)
            name = os.path.splitext(file_name)[0]
            self.import_from_file(account_file, name)

    def import_from_file(self, account_file: str, account_name: str):
        print(account_file, account_name)
        account = pytezos.using(
            key = account_file,
            shell = self.endpoint,
        )
        if account_name in self.accounts:
            print(f"user {account_name} as aready been imported")
            return
        print(f"user {account_name} as aready been imported")
        self.accounts[account_name] = account

    def import_to_tezos_client(self, account_name: str):
        """
        Import_account
        """
        env = dict(os.environ)
        host = self.endpoint
        print(self.account)
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
        operation = self.accounts[account_name].activate_account()
        submit_transaction(operation, self.accounts[account_name])


    def reveal_account(self, account_name: str):
        """
        Reveal account
        """
        operation = self.accounts[account_name].reveal()
        submit_transaction(operation, self.accounts[account_name])

    def get_account(self, account_name: str):
        """
        Return account for account
        """
        return self.accounts[account_name]

    def get_contracts(self, contract: str):
        contract_clients = {}
        for account in self.accounts:
            self.accounts(contract)
        return contract_clients
