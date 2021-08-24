import os.path
from datetime import datetime

from pytezos import pytezos, ContractInterface
from pytezos.operation.result import OperationResult

from src.compile import *
from src.utils import submit_transaction, print_error

from loguru import logger


from time import sleep


admin = {
        'pkh': 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb',
        'sk': 'edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq',
        'pk': 'edpkvGfYw3LyB1UcCahKQk4rF2tvbMUk8GFiTuMjL75uGXrpvKXhjn',
}

stablecoin_path = 'prediction-market-contracts/src/contracts/third-party'
contract_path = 'prediction-market-contracts-lazy/'

USDtzLeger = {
        'path': stablecoin_path + '/FA12Permissive.ligo',
        'storage': {
            'totalSupply': 0,
            'ledger': {
                admin['pkh']: {
                    'balance': 2**65,
                    'allowances': {}
                }
            }
        }
}


binary_contract = {
    'path': contract_path + 'container/main.mligo.m4',
    'storage': {
        'lambda_repository':
            {
                'creator': 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb',
                'lambda_map': {}
            },
        'business_storage': {
            'tokens': {'ledger_map': {}, 'supply_map': {}},
            'markets': {
				'market_map': {},
				'liquidity_provider_map': {},
				'create_restrictions': {
					'creator_address': None,
					'currency': None
				}
			}
        }
    }
}

helper_directory = contract_path + 'm4_helpers'

shell = 'http://localhost:20000'


def wait_next_block(block_time, client):
    header = client.shell.head.header()
    block_hash = client.shell.head.hash()
    prev_block_dt = datetime.strptime(header['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    elapsed_sec = (datetime.utcnow() - prev_block_dt).seconds
    delay_sec = 0 if elapsed_sec > block_time else block_time - elapsed_sec
    logger.debug(f'Wait {delay_sec} seconds until block {block_hash} is finalized')
    for i in range(block_time):
        current_block_hash = client.shell.head.hash()
        if current_block_hash == block_hash:
            sleep(1)
        else:
            return current_block_hash


def get_contract_id(client, block_time, opg_hash, num_block_wait=10):
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
        logger.debug(i)
        try:
            pending_opg = client.shell.mempool.pending_operations[opg_hash]
            if not OperationResult.is_applied(pending_opg):
                raise Exception("Operation is pending")
            logger.debug(f'Still in mempool: {opg_hash}')
        except StopIteration:
            res = client.shell.blocks[-(i + 1):].find_operation(opg_hash)
            if not OperationResult.is_applied(res):
                raise Exception("Operation was not applied")
            metadata = res['contents'][0]['metadata']
            contract_id = metadata['operation_result']['originated_contracts'][0]
            if contract_id is None:
                raise
            return contract_id


def deploy_from_file(file, key, wrkdir="", storage=None, shell=shell, get_contract=False):
    """
    Compile and deploy a ligo contract

    :param file: path the the ligo file
    :param key: account key for the deployer
    :param storage: storage for the file contract
    :param shell: where to deploy the contract
    :return:
    """
    contract = compile_contract(file, wrkdir)
    logger.debug(contract)
    logger.debug(storage)
    ci = ContractInterface.from_michelson(contract)
    #Doing this in two time seems to create better results
    client = pytezos.using(shell=shell).using(key=key)
    logger.info(storage)
    operation = client.origination(script=ci.script(initial_storage=storage))
    res = submit_transaction(operation)
    if res is not None and res["hash"] and get_contract is True:
        return get_contract_id(client, 3, res["hash"])


def deploy_stablecoin(key=admin['sk'], shell=shell, wrkdir=stablecoin_path, storage=USDtzLeger):
    wrkdir = os.path.abspath(wrkdir)
    file_path = os.path.abspath(USDtzLeger['path'])
    stablecoin_id = deploy_from_file(file_path, key, wrkdir, storage['storage'], shell, get_contract=True)
    if stablecoin_id is None:
        raise Exception("deploiement failed")
    logger.debug(f"stablecoin was deployed at {stablecoin_id}")
    return stablecoin_id


def deploy_lambdas(path: str, contract_id: str, compiled_path='compiled_contracts', shell=shell, key=admin['sk']):
    transactions = []
    client = pytezos.using(shell=shell).using(key=key)
    contract = client.contract(contract_id)
    for file in os.listdir(path):
        macro_filepath = f'{path}/{file}'
        logger.error(macro_filepath)
        content = preprocess_file(macro_filepath, helper_directory)
        file_name = os.path.splitext(file)[0]
        filepath = f"{compiled_path}/{file_name}"
        write_to_file(content, filepath)
        logger.info(f"{filepath} was generated")
        content = compile_expression(filepath)
        file_name = os.path.splitext(file_name)[0]
        operation = contract.installLambda({'name': file_name, 'code': content})
        res = submit_transaction(operation.as_transaction(), error_func=print_error)
        logger.info(f"{filepath} lambda is deployed")
    operation = contract.sealContract()
    submit_transaction(operation.as_transaction())


def deploy_market(key=admin['sk'], shell=shell, contract_path=contract_path, storage=binary_contract):
    """
    Deploy the complete market on the specified shell

    :param key:
    :return: None
    """
    logger.debug("deploying binary market")
    content = preprocess_file(binary_contract['path'], helper_directory)
    path = "compiled_contracts"
    try:
        os.mkdir(path)
    except OSError:
        logger.debug("Creation of the directory %s failed" % path)
    else:
        logger.debug("Successfully created the directory %s " % path)
    filepath = f"{path}/main.mligo"
    write_to_file(content, filepath)
    wrkdir = os.path.abspath('.')
    logger.error(storage)
    market_id = deploy_from_file(filepath, key, wrkdir=wrkdir, storage=storage['storage'], shell=shell, get_contract=True)
    if market_id is None:
        raise Exception("deploiement failed")
    lazy_contracts_path = contract_path + '/lazy/lazy_lambdas'
    deploy_lambdas(lazy_contracts_path, market_id, compiled_path=path, shell=shell, key=key)
    logger.debug(f"Binary market was deployed at {market_id}")
    print(f"Binary market was deployed at {market_id}")
    return market_id
