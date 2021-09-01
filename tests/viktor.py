from tests.conftest import market
from pytezos import pytezos
from src.config import Config
from src.utils import get_public_key, get_stablecoin, get_tokens_id_list, print_error, submit_transaction

def start(config_file, contract_id, stablecoin_id):
    config = Config(
        config_file=config_file,
        contract=contract_id
    )
    # tokens = get_tokens_id_list(market_id)
    config = config
    account = config.get_admin_account()
    contract = account.contract(contract_id)
    stablecoin = account.contract(stablecoin_id)
    buis_storage = contract.storage["business_storage"]
    markets = buis_storage["markets"]
    market_map = markets['market_map']
    ledger_map = buis_storage['tokens']['ledger_map']
    supply_map = buis_storage['tokens']['supply_map']
    
    return {
            "config": config,
            "contract": contract,
            "client": account,
            "stablecoin": stablecoin,
            "business_storage": buis_storage,
            "markets": markets,
            "market_map": market_map,
            "ledger_map": ledger_map,
            "supply_map": supply_map
    }


 
