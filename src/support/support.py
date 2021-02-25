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

from utils import summary
from utils.utils import get_stablecoin, get_public_key

from src.utils import summary
from src.utils.utils import get_stablecoin, get_public_key

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

    def activate_user(self, user: str):
        """
        Activate user
        """
        print(f"Trying to activate account of user {user}: ", end='')
        try:
            self.accounts[user].activate_account().autofill().sign().inject()
            print(f"account of {user} was activated")
        except Exception as e:
            print(e)
            print(f"account of user {user} was not activated")

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

    def reveal_user(self, user: str):
        """
        Reveal user
        """
        print(f"Trying to reveal account of user {user}: ", end='')
        try:
            self.accounts[user].reveal().autofill().sign().inject()
            print(f" account of user {user} was revealed")
        except Exception:
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
        auction_end_date: int,
        market_end_date: int
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
        self.pm_contracts[user].createQuestion({
            'auction_end': int(auction_end_date.timestamp()),
            'market_close': int(market_close_date.timestamp()),
            'quantity': quantity,
            'question': ipfs_hash,
            'rate': rate
        }).as_transaction().autofill().sign().inject()
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
        ##Got the stablecoin ?? Rethink the question??
        ####Check if the account is filled (check the balancebefore)
        ####With the correct value
        stablecoin = get_stablecoin(admin_account, self.contract)
        stablecoin.transfer({
            'from': get_public_key(admin_account),
            'to': get_public_key(self.get_account(user)),
            'value': value
        }).as_transaction().autofill().sign().inject()

    def bid_auction(
            self,
            ipfs_hash: str,
            user: str,
            quantity: int,
            rate: int
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
        result = self.pm_contracts[user].bid(_data).as_transaction() \
            .autofill(gas_reserve=200000).sign().inject()
        print(result)
        return result


    def close_auction(self, ipfs_hash: str, user):
        """
        Close the auction

        ipfs_hash: the hash of the concerned contract
        """
        #####Check if the contract is close
        self.pm_contracts[user].closeAuction(ipfs_hash).as_transaction() \
                .autofill().sign().inject()
    
    def buy_token(
            self,
            question: str,
            token_type: bool,
            coin_quantity: int,
            user: str):
        """
        Buy the token

        question:
        token_type;
        coin_quantity:
        user
        """
        self.pm_contracts[user].buyToken(
                question,
                token_type,
                coin_quantity,
                user
            ).as_transaction().autofill().sign().inject()

    def close_market(
            self,
            question: str,
            is_yes: bool,
            user: str
        ):
        self.pm_contracts[user].close_market(
            question,
            is_yes
        ).as_transaction().autofill.sign().inject()
    

"""
    def burn(
            self,
            question: str,
            token_quantity: int,
            user: str
        ):
        self.pm_contracts[user].burn(
                question,
                token_quantity
            ).as_transaction().autofill.sign.inject()

    def claim_winnings(
            self,
            question: str,
            user: str
        ):
        self.pm_contracts[user].claimWinnings(
                question
            ).as_transaction().autofill.sign().inject()
"""
def transfer_stablecoin_to_user(
        dest: str,
        src: str,
        value: int
    ):
    """
    Transfer a certain amount of stablcoins towards an user address

    user address that will receive the funds
    """
    admin_account = summary.admin_account()
    stablecoin = get_stablecoin(admin_account, self.contract)
    stablecoin.transfer({
        'from': src,
        'to': dest,
        'value': value
    }).as_transaction().autofill().sign().inject()
