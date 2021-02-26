"""
Support management helper
"""
import configparser
import json
import os
import subprocess
from datetime import datetime, timedelta

import ipfshttpclient
import pytz
from pytezos import pytezos
from pytezos.rpc.node import RpcError

from src.utils import summary
from src.utils.utils import get_stablecoin, get_public_key

def submit_transaction(transaction, account, count=None, tries=None):
    transaction.autofill(counter=count,branch_offset=1).sign().inject()
    #try: 
    #except RpcError as e:
    #    error_type = e[0][id]
    #    if error_type == 'proto.008-PtEdo2Zk.contract.counter_in_the_future':
    #    operation.as_transaction().autofill(counter=count,branch_offset=1).sign().inject()

class Support:
    """
    Support Class
    """
    def __init__(self, users: list, config_file="./oracle.ini", user_folder="users"):
        """
        Create a Support object

        users: List of users who require support
        """
        self.config = configparser.ConfigParser()
        try:
            self.config.read(config_file)
        except Exception:
            print("Missing oracle.ini file")
        self.contract = self.config['Tezos']['pm_contract']
        self.accounts = {}
        self.pm_contracts = {}
        self.users = users
        self.instantiate_users(self.users, user_folder)

    def instantiate_users(self, users: list, user_folder: str):
        """
        Get all the user data from the user folder user
        """
        for user in self.users:
            self.accounts[user] = pytezos.using(
                key = f"{user_folder}/{user}.json",
                shell = self.config['Tezos']['endpoint'],
            )
            self.pm_contracts[user] = self.accounts[user].contract(
                    self.contract
            )

    def import_user(self, user: str):
        """
        Import_user
        """
        print(f"Trying to import account of user {user}: ", end='')
        env = dict(os.environ)
        host = self.config['Tezos']['endpoint']
        subprocess.run(
            [
                'tezos-client',
                '-E',
                host,
                'import',
                'secret',
                'key',
                user,
                f"unencrypted:{self.accounts[user].key.secret_key()}",
                '--force'
            ],
            env=env,
            check=False,
        )
        print(f"account of {user} was imported")

    def activate_user(self, user: str):
        """
        Activate user
        """
        print(f"Trying to activate account of user {user}: ", end='')
        try:
            operation = self.accounts[user].activate_account()
            submit_transaction(operation, self.accounts[user])
            print(f"account of {user} was activated")
        except Exception as e:
            print(e)
            print(f"account of user {user} was not activated")


    def reveal_user(self, user: str):
        """
        Reveal user
        """
        print(f"Trying to reveal account of user {user}: ", end='')
        try:
            operation = self.accounts[user].reveal()
            submit_transaction(operation, self.accounts[user])
            print(f" account of user {user} was revealed")
        except Exception as e:
            print(e)
            print(f"account of user {user} was not revealed")

    def get_account(self, user: str):
        """
        Return account for user
        """
        return self.accounts[user]

    def ask_question(
        self,
        question: str,
        answer: str,
        user: str,
        quantity: int,
        rate: int,
        auction_end_date: int = 5,
        market_end_date: int = 10
        ):
        """
        Create a question in IPFS

        question: string representing the answer asked
        answer: string representing the possible answer
        user: string representing the questions owner
        quantity: integer representing the quantity of stable coin generated
        rate: rate
        """
        if user not in self.users:
            raise Exception("Missing User")
        timenow = datetime.now().astimezone(pytz.utc)
        auction_end_date = timenow + timedelta(minutes=auction_end_date)
        market_close_date = timenow + timedelta(minutes=market_end_date)
        param = {
                'auctionEndDate': auction_end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                'iconURL':
                'https://images-na.ssl-images-amazon.com/images/I/41GqyirrgbL._AC_SX425_.jpg',
                'marketCloseDate': market_close_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                'question': question,
                'yesAnswer': answer,
        }
        ipfs = ipfshttpclient.connect(self.config['IPFS']['server'])
        ipfs_hash = ipfs.add_str(json.dumps(param))
        print(f"Created hash {ipfs_hash}")
        print(ipfs.get_json(ipfs_hash))
        operation = self.pm_contracts[user].createQuestion({
            'auction_end': int(auction_end_date.timestamp()),
            'market_close': int(market_close_date.timestamp()),
            'quantity': quantity,
            'question': ipfs_hash,
            'rate': rate
        })
        submit_transaction(operation.as_transaction(), self.pm_contracts[user])
        print(f"Created market {ipfs_hash} in PM contract")
        return ipfs_hash

    def transfer_stablecoin_to_user(
            self,
            user: str,
            value: int
        ):
        """
        Transfer a certain amount of stablcoins towards an user address

        user address that will receive the funds
        """
        admin_account = summary.admin_account()
        stablecoin = get_stablecoin(admin_account, self.contract)
        operation = stablecoin.transfer({
            'from': get_public_key(admin_account),
            'to': get_public_key(self.get_account(user)),
            'value': value
        })
        submit_transaction(operation.as_transaction(), admin_account)

    def bid_auction(
            self,
            ipfs_hash: str,
            user: str,
            quantity: int = 5,
            rate: int = 10
        ):
        """
        Launch a bid on an auction

        ipfs_hash: the contract concerned by the bid
        user: string representing the user which is bidding during the auction
        quantity: Integer representing quantity of stable coins bid during the auction
        rate: What is rate?
        """
        print(f"User {user} bidding {rate} on {ipfs_hash}")
        _data = {
                'quantity': quantity,
                'question': ipfs_hash,
                'rate': rate
        }
        operation = self.pm_contracts[user].bid(_data)
        result = submit_transaction(operation.as_transaction(), self.pm_contracts[user])


    def close_auction(self, ipfs_hash: str, user):
        """
        Close the auction

        ipfs_hash: the hash of the concerned contract
        user: user closing the auction (owner)
        """
        #####Check if the contract is close
        operation = self.pm_contracts[user].closeAuction(ipfs_hash)
        submit_transaction(operation.as_transaction(), self.pm_contracts[user])
    
    def buy_token(
            self,
            question: str,
            token_type: bool,
            token_quantity: int,
            user: str):
        """
        Buy the token

        question: Concerned question
        token_type: type of tokens (yes or no)
        token_quantity: quantity of tokens to buy
        user: user buying the tokens
        """
        operation = self.pm_contracts[user].buyToken(
                question,
                token_type,
                token_quantity,
                user
            )
        submit_transaction(operation.as_transaction(), self.pm_contracts[user])

    def close_market(
            self,
            question: str,
            token_type: bool,
            user: str
        ):
        """
        Close the market

        ipfs_hash: the hash of the concerned contract
        token_type: type of tokens (yes or no)
        user: user closing the market (owner)
        """
        operation = self.pm_contracts[user].closeMarket(
            question,
            token_type
        )
        submit_transaction(operation.as_transaction(), self.pm_contracts[user])
    
    def burn(
            self,
            question: str,
            token_quantity: int,
            user: str
        ):
        """
        Burn the token

        question: Concerned question
        coin_quantity: quantity of tokens to burn
        user: user buying the tokens
        """
        operation = self.pm_contracts[user].burn(
                question,
                token_quantity
        )
        submit_transaction(operation.as_transaction(), self.pm_contracts[user])

    def claim_winnings(
            self,
            question: str,
            user: str
        ):
        operation = self.pm_contracts[user].claimWinnings(
                question
        )
        submit_transaction(operation.as_transaction(), self.pm_contracts[user])
