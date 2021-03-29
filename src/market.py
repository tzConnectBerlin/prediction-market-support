"""
Market management helper
"""
import json
from datetime import datetime, timedelta

import ipfshttpclient
import pytz

from src.accounts import Accounts
from src.config import Config
from src.utils import get_public_key, get_stablecoin, print_error, submit_transaction


class Market:
    """
    Market Class
    """

    def __init__(self, accounts: Accounts, config: Config):
        """
        Create a Market object

        users: List of users who require market
        """
        self.accounts = accounts
        self.config = config
        self.contract = self.config['contract']
        self.pm_contracts = accounts.contract_accounts(self.contract)

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
        ipfs = ipfshttpclient.connect(self.config['ipfs_server'])
        ipfs_hash = ipfs.add_str(json.dumps(param))
        operation = self.pm_contracts[user].createQuestion({
            'auction_end': int(auction_end_date.timestamp()),
            'market_close': int(market_close_date.timestamp()),
            'quantity': quantity,
            'question': ipfs_hash,
            'rate': rate
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)
        return ipfs_hash

    def transfer_stablecoin_to_user(
            self,
            user: str,
            value: int
    ):
        """
        Transfer a certain amount of stablecoin towards an user address

        user address that will receive the funds
        """
        stablecoin = get_stablecoin(self.config["admin_account"], self.contract)
        operation = stablecoin.transfer({
            'from': get_public_key(self.config["admin_account"]),
            'to': get_public_key(self.accounts[user]),
            'value': value
        })
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def fund_stablecoin(
            self,
            value: int
    ):
        """
        fund all accounts with a random quantity of stablecoin

        value: the amont of stablecoin funded
        """
        operations_list = []
        if len(self.accounts.names()) == 0:
            return
        stablecoin = get_stablecoin(self.config["admin_account"], self.contract)
        for user in self.accounts.names():
            operation = stablecoin.transfer({
                'from': get_public_key(self.config["admin_account"]),
                'to': get_public_key(self.accounts[user]),
                'value': value
            })
            operations_list.append(operation.as_transaction())
        bulk_operations = self.config["admin_account"].bulk(*operations_list)
        submit_transaction(bulk_operations, error_func=print_error)

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
        data = {
            'quantity': quantity,
            'question': ipfs_hash,
            'rate': rate
        }
        operation = self.pm_contracts[user].bid(data)
        submit_transaction(operation.as_transaction())

    def multiple_bids(
            self,
            ipfs_hash: str,
            quantity: int = 5,
            rate: int = 10
    ):
        """
        Launch multiples bid on a auction for all of the user contained in the accounts Class

        ipfs_hash: Contract on which the bid are made
        """
        operations_list = []
        for user in self.accounts.names():
            data = {
                'quantity': quantity,
                'question': ipfs_hash,
                'rate': rate
            }
            operation = self.pm_contracts[user].bid(data)
            operations_list.append(operation.as_transaction())
        bulk_operations = self.config["admin_account"].bulk(*operations_list)
        submit_transaction(bulk_operations, error_func=print_error)

    def close_auction(self, ipfs_hash: str, user):
        """
        Close the auction

        ipfs_hash: the hash of the concerned contract
        user: user closing the auction (owner)
        """
        operation = self.pm_contracts[user].closeAuction(ipfs_hash)
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def withdraw_auction(
            self,
            question: str,
            user: str
    ):
        operation = self.pm_contracts[user].withdrawAuction(
            question
        )
        submit_transaction(operation.as_transaction(), error_func=print_error)

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
        res = submit_transaction(operation.as_transaction(), error_func=print_error)
        print(res)

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
        submit_transaction(operation.as_transaction(), error_func=print_error)

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
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def claim_winnings(
            self,
            question: str,
            user: str
    ):
        operation = self.pm_contracts[user].claimWinnings(
            question
        )
        submit_transaction(operation.as_transaction(), error_func=print_error)

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
        submit_transaction(operation.as_transaction(), error_func=print_error)

    def swap(
            self,
            question: str,
            token_in_type: bool,
            fixed_token_in: int,
            user: str
    ):
        operation = self.pm_contracts[user].swap(
            question,
            token_in_type,
            fixed_token_in
        )
        submit_transaction(operation.as_transaction(), error_func=print_error)
