"""
Market management helper
"""
import json
import random
import time
from datetime import datetime, timedelta

from loguru import logger

from src.accounts import Accounts
from src.config import Config
from src.utils import get_public_key, get_stablecoin, get_tokens_id_list, print_error, submit_transaction

logger = logger.opt(colors=True)


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

    def pm_contracts(
            self,
            user: str
    ):
        return self.accounts[user].contract(self.contract)

    def ask_question(
            self,
            question: str,
            answer: str,
            user: str,
            quantity: int,
            rate: int,
            ipfs_hash: str,
            auction_end_date: datetime = (datetime.now() + timedelta(minutes=5)),
            market_id: int = None,
            token_contract: str = None
    ):
        """
        Create a new prediction market

        question: string representing the answer asked
        answer: string representing the possible answer
        user: string representing the questions owner
        quantity: integer representing the quantity of stable coin generated
        rate: rate
        """
        if token_contract is None:
            token_contract = self.config['stablecoin']
        if market_id is None:
            market_id = random.randint(10, 2**63)
        #Fully featured api / Created default for ipfs and timestamp but make sure it is starting point
        if type(token_contract) is str:
            currency = {'fa12': token_contract}
        else:
            currency = {
                'fa2': {
                    'token_address': token_contract[0],
                    'token_id': token_contract[1]
                }
            }
        operation = self.pm_contracts(user).marketCreate({
            'auction_period_end': int(auction_end_date),
            'bet': {
                'quantity': quantity,
                'predicted_probability': rate
            },
            'market_id': market_id,
            'metadata': {
                'ipfs_hash': ipfs_hash,
                'adjudicator': get_public_key(self.accounts[user]),
                'currency': currency,
                'description': 'Question: ' + question + ' Answer: ' + answer
            }
        })
        return market_id, operation.as_transaction()

    def bid_auction(
            self,
            market_id: int,
            user: str,
            quantity: int = 5,
            rate: int = 10
    ):
        """
        Launch a bid on an auction

        market_id: the market concerned by the bid
        user: string representing the user which is bidding during the auction
        quantity: Integer representing quantity of stable coins bid during the auction
        rate: What is rate?
        """
        data = {
            'market_id': market_id,
            'bet': {
                'quantity': quantity,
                'predicted_probability': rate
            }
        }
        operation = self.pm_contracts(user).auctionBet(data)
        return operation.as_transaction()

    def auction_clear(
            self,
            market_id: int,
            user
    ):
        """
        Clear the market

        """
        operation = self.pm_contracts(user).auctionClear(market_id)
        return operation.as_transaction()

    def auction_withdraw(
            self,
            market_id: int,
            user
    ):
        """
        Withdraw allocated tokens from a bet in the auction


        """
        operation = self.pm_contracts(user).auctionWithdraw(market_id)
        return operation.as_transaction()

    def market_enter_exit(
            self,
            market_id: int,
            user,
            direction: str,
            amount: int
    ):
        """
        Enter or exit the market by minting or burning outcome token pairs in exchange for market currency tokens
        """
        data = {
            'direction': direction,
            'params': {
                'market_id': market_id,
                'amount': amount
            }
        }
        operation = self.pm_contracts(user).marketEnterExit(data)
        return operation.as_transaction()

    def multiple_bids(
            self,
            market_id: int,
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
                'market_id': market_id,
                'bet': {
                    'quantity': quantity,
                    'predicted_probability': rate
                }
            }
            operation = self.pm_contracts(user).auctionBet(data)
            operations_list.append(operation.as_transaction())
        bulk_operations = self.config["admin_account"].bulk(*operations_list)
        return bulk_operations

    def withdraw_auction(
            self,
            question: str,
            user: str
    ):
        """
        Take an alllocation and withdraw the tokens attributed to you

        """
        operation = self.pm_contracts(user).withdrawAuction(
            question
        )
        return operation.as_transaction()

    def close_market(
            self,
            market_id: int,
            user: str,
            token_type: bool
    ):
        """
        Close the market

        market_id: the hash of the concerned contract
        token_type: type of tokens (yes or no)
        user: user closing the market (owner)
        """
        winning_prediction = 'yes' if token_type is True else 'no'
        operation = self.pm_contracts(user).marketResolve({
            'market_id': market_id,
            'winning_prediction': winning_prediction
        })
        return operation.as_transaction()

    def mint(
            self,
            market_id: int,
            user: str,
            amount: int
    ):
        """
        Mint the token

        question: Concerned question
        token_type: type of tokens (yes or no)
        token_quantity: quantity of tokens to buy
        user: user whose token are bought
        """
        operation = self.pm_contracts(user).marketEnterExit({
            'direction': 'payIn',
            'params': {
                'market_id': market_id,
                'amount': amount
            }
        }
        )
        return operation.as_transaction()

    def burn(
            self,
            market_id: int,
            user: str,
            amount: int
    ):
        """
        Burn the token

        question: Concerned question
        coin_quantity: quantity of tokens to burn
        user: user buying the tokens
        """
        operation = self.pm_contracts(user).marketEnterExit({
            'direction': 'payOut',
            'params': {
                'market_id': market_id,
                'amount': amount
            }
        }
        )
        return operation.as_transaction()

    def claim_winnings(
            self,
            market_id: int,
            user: str
    ):
        """
        Claim winnings

        question: Concerned question
        user: user owning the winning tokens
        """
        operation = self.pm_contracts(user).claimWinnings(
            market_id
        )
        return operation.as_transaction()

    def update_liquidity(
            self,
            market_id: int,
            user: str,
            direction: str,
            amount: int
    ):
        """
        Update the liquidity for the market

        user:
        direction: Union type of the following options add the liquidity
        payIn to add liquidity to the pool to payOut remove liquidity
        from the pool
        amount: The amount of liquidity tokens to receive or burn
        """
        operation = self.pm_contracts(user).swapLiquidity({
            'direction': direction,
            'params': {
                'market_id': market_id,
                'amount': amount
            }
        })
        return operation.as_transaction()

    def swap_tokens(
            self,
            market_id: int,
            user: str,
            token_to_sell: str,
            amount: int
    ):
        """
        Swap one outcome token through the liquidity pool for its opposing pair
        as a fixed input swap operation

        market_id: id of the concerned market
        token_to_sell: the type of token to sell (yes or no)
        amount: the amount to token to sell
        """
        operation = self.pm_contracts(user).swapTokens({
            'token_to_sell': token_to_sell,
            'params': {
                'market_id': market_id,
                'amount': amount
            }
        })
        return operation.as_transaction()

    def get_storage(
            self,
            market_id: int,
            user: str,
    ):
        time.sleep(1)
        tokens = get_tokens_id_list(market_id)
        logger.error(market_id)
        market_map = self.get_market_map_storage(market_id, user)
        liquidity_provider_map = self.get_liquidity_provider_map_storage(market_id, user)
        supply_map = self.get_supply_map_storage(user, tokens)
        ledger_map = self.get_ledger_map_storage(user, tokens)
        return {
            'market_map': market_map,
            'liquidity_provider_map': liquidity_provider_map,
            'supply_map': supply_map,
            'ledger_map': ledger_map
        }
        
    def get_market_map_storage(self, market_id: int, user: str):
        try:
            market_map = self.pm_contracts(user).storage['business_storage']['markets']['market_map'][market_id]()
        except:
            logger.error(
                f"\ndoes not exist in market_map, <green>market_id</> = {market_id}"
            )
            return None
        return market_map

    def get_liquidity_provider_map_storage(self, market_id: int, user: str):
        try:
            map_key = {
                'originator': get_public_key(self.accounts[user]),
                'market_id': market_id
            }
            liquidity_provider_map = self.pm_contracts(
                user
            ).storage['business_storage']['markets']['liquidity_provider_map'][map_key]()
            return liquidity_provider_map
        except:
            logger.error(
                f"\ncan't get liquidity_provider_map for market_id = {market_id} and user = {user}"
            )
            return None

    def get_ledger_map_storage(self, user: str, tokens: list):
        ledger_map = {}
        user_address = get_public_key(self.accounts[user])
        for token in tokens:
            map_key = {'owner': user_address, 'token_id': token['token_value']}
            entry = self.pm_contracts(user).storage['business_storage']['tokens']['ledger_map']
            try:
                ledger_map[token['token_name']] = entry[token['token_value']]()
            except:
                ledger_map[token['token_name']] = 'Not available in ledger_map'
        return ledger_map

    def get_supply_map_storage(self, user: str, tokens: list):
        supply_map = {}
        for token in tokens:
            entry = self.pm_contracts(user).storage['business_storage']['tokens']['supply_map']
            try:
                supply_map[token['token_name']] = entry[token['token_value']]()
            except:
                supply_map[token['token_name']] = 'Not available in supply_map'
        if supply_map == {}:
            return None
        return supply_map