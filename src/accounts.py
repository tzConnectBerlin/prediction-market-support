import json
import os
import subprocess

import glob
from pytezos import pytezos, Key

from src.utils import submit_transaction, get_tezos_client_path


class Accounts:
    """
    User Class for Handling tezos accounts
    """

    def __init__(self, endpoint):
        self.accounts = {}
        self.endpoint = endpoint

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
            key=account_data,
            shell=self.endpoint,
        )
        self.accounts[account_name] = account

    def import_from_tezos_client(self, ignored_accounts=[], client_path='~/.tezos-client'):
        """
        Import account from tezos client
        """
        path = os.path.join(get_tezos_client_path(client_path), 'secret_keys')
        with open(path, 'r') as f:
            try:
                data = json.loads(f.read())
            except:
                raise Exception('there is something wrong with the key file')
        for x in data:
            if x['name'] not in ignored_accounts:
                prefix, sk = x['value'].split(':', maxsplit=1)
                try:
                    self.import_from_file(Key.from_encoded_key(sk), x['name'])
                except:
                    print(f'something went wrong with account {x["name"]}')

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
