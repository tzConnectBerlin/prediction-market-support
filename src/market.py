"""
Market management helper
"""
import configparser
import json
from datetime import datetime, timedelta

import ipfshttpclient
import pytz
from pytezos import pytezos
from pytezos.rpc.node import RpcError

from src.accounts import Accounts
from src.config import Config
from src.utils import summary
from src.utils.utils import get_public_key, get_stablecoin, submit_transaction

class Market:
    """
    Market Class
    """
    def __init__(self, accounts: Accounts, config):
        """
        Create a Market object

        users: List of users who require market
        """
        self.contract = self.config['Tezos']['pm_contract']
        self.pm_contracts = accounts.contract_accounts(self.contract)
        print(self.pm_contracts)

    def ask_question(
        self,
        question: str,
        answer: str,
        user: str,
        quantity: int,
        rate: int,
        auction_end_date: float = 5.0,
        market_end_date: float = 10.0
        ):
        """
        Create a question in IPFS

        question: string representing the answer asked
        answer: string representing the possible answer
        user: string representing the questions owner
        quantity: integer representing the quantity of stable coin generated
        rate: rate
        """
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
        #print(f"Created hash {ipfs_hash}")
        #print(ipfs.get_json(ipfs_hash))
        operation = self.pm_contracts[user].createQuestion({
            'auction_end': int(auction_end_date.timestamp()),
            'market_close': int(market_close_date.timestamp()),
            'quantity': quantity,
            'question': ipfs_hash,
            'rate': rate
        })
        submit_transaction(operation.as_transaction(), self.pm_contracts[user])
        #print(f"Created market {ipfs_hash} in PM contract")
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
            'to': get_public_key(self.accounts[user]),
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
        data = {
                'quantity': quantity,
                'question': ipfs_hash,
                'rate': rate
        }
        operation = self.pm_contracts[user].bid(data)
        result = submit_transaction(operation.as_transaction(), self.pm_contracts[user])
    
    def withdraw_auction(
            self,
            question: str,
            user: str
        ):
        operation = self.pm_contracts[user].withdrawAuction(
                question
        )
        submit_transaction(operation.as_transactions(), self.pm_contracts[user])


    def close_auction(self, ipfs_hash: str, user):
        """
        Close the auction

        ipfs_hash: the hash of the concerned contract
        user: user closing the auction (owner)
        """
        operation = self.pm_contracts[user].closeAuction(ipfs_hash)
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
        user: user whose token are bought
        """
        operation = self.pm_contracts[user].buyToken(
                question,
                token_type,
                token_quantity
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

    def update_liquidity(
            self,
            question: str,
            add_lqt: bool,
            lqt_amount: int,
            user: str
        ):
        operation = self.pm_contracts[user].updateLiquidity(
                question,
                add_lqt,
                lqt_amount
        )
        submit_transaction(operation.as_transaction(), self.pm_contracts[user])

    def swap(
            self,
            questions: str,
            token_in_type: bool,
            fixed_token_in: int,
            user: str
        ):
        operation = self.pm_contracts[user].swap(
                question,
                token_in_type,
                fixed_token_in
        )
        submit_transaction(operation.as_transaction(), self.pm_contracts[user])
