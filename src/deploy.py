import os.path
from datetime import datetime

from pytezos import pytezos, ContractInterface
from pytezos.operation.result import OperationResult

from src.compile import *
from src.utils import submit_transaction

from time import sleep

admin = {
        'pkh': 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb',
        'sk': 'edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq',
        'pk': 'edpkvGfYw3LyB1UcCahKQk4rF2tvbMUk8GFiTuMjL75uGXrpvKXhjn',
}

Migration = {
        'path': 'contracts/Migrations.ligo',
        'storage': {
            'last_completed_migration': 0,
            'owner': admin['pkh']
            }
        }

USDtzLeger = {
        'path': 'contracts/third-party/FA12Permissive.ligo',
        'storage': {
            'totalSupply': 0,
            'ledger': {
                admin['pkh']: {
                    'balance': 100000000000000000000,
                    'allowances': {}
                }
            }
        }
}

Market = {
        'path': 'contracts/Market.mligo',
        'storage': {
        'last_token_created': 0,
        'owner': admin['pkh'],
        'questions': {},
        'stablecoin': 'KT1VK3kD6Xu7rmmD467M168rcR3Th82HbLra',
        'tokens': {
            'ledger': {},
            'operators': {},
            'token_metadata': {},
            'token_total_supply': {},
        }
    }
}


def wait_next_block(block_time, client):
    header = client.shell.head.header()
    block_hash = client.shell.head.hash()
    prev_block_dt = datetime.strptime(header['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    elapsed_sec = (datetime.utcnow() - prev_block_dt).seconds
    delay_sec = 0 if elapsed_sec > block_time else block_time - elapsed_sec
    print(f'Wait {delay_sec} seconds until block {block_hash} is finalized')
    for i in range(block_time):
        current_block_hash = client.shell.head.hash()
        if current_block_hash == block_hash:
            sleep(1)
        else:
            return current_block_hash


def get_contract_id(client, block_time, opg_hash, num_block_wait=5):
    """
    Return an hash for the deployed contract given a operation hash

    :param client: client for the current chains
    :param block_time: time between blocks baking
    :param opg_hash: hash of the operation injected
    :param num_block_wait: Num of blocks to wait until failing
    :return:
    """
    for i in range(num_block_wait):
        wait_next_block(block_time, client)
        try:
            pending_opg = client.shell.mempool.pending_operations[opg_hash]
            if not OperationResult.is_applied(pending_opg):
                raise Exception("Operation is pending")
            print(f'Still in mempool: {opg_hash}')
        except StopIteration:
            res = client.shell.blocks[-(i + 1):].find_operation(opg_hash)
            if not OperationResult.is_applied(res):
                raise Exception("Operation was not applied")
            metadata = res['contents'][0]['metadata']
            contract_id = metadata['operation_result']['originated_contracts'][0]
            return contract_id


def deploy_from_file(file, key, storage=None, shell="http://localhost:20000"):
    """
    Compile and deploy a ligo contract

    :param file: path the the ligo file
    :param key: account key for the deployer
    :param storage: storage for the file contract
    :param shell: where to deploy the contract
    :return:
    """
    contract = compile_contract(file)
    ci = ContractInterface.from_michelson(contract)
    client = pytezos.using(shell=shell, key=key)
    operation = client.origination(script=ci.script(initial_storage=storage))
    res = submit_transaction(operation)
    if res is not None and res["hash"]:
        return get_contract_id(client, 2, res["hash"])


def deploy_market(key=admin['sk'], shell="http://localhost:20000"):
    """
    Deploy the complete market on the specified shell

    :param key:
    :return: None
    """
    print("deploying markets")
    stablecoin_id = deploy_from_file(USDtzLeger['path'], key, USDtzLeger['storage'])
    print(f"stablecoin was deployed at {stablecoin_id}")
    Market['storage']['stablecoin'] = stablecoin_id
    print(Market)
    print("market was deployed")
    market_id = deploy_from_file(Market['path'], key, Market['storage'])
    return market_id
