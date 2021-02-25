from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from subprocess import Popen, PIPE
from time import sleep

from pytezos import pytezos, ContractInterface, Key, OperationResult
from requests.exceptions import ConnectionError

ligo_cmd = (
        f'docker run --rm -v "$PWD":"$PWD" -w "$PWD" ligolang/ligo:0.7.1 "$@"'
)

shell="http://localhost:20000"

key="edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq"

client = pytezos.using(
    shell=shell,
    key=Key.from_encoded_key(
        key
    )
)

owner = client.key.public_key_hash()

wolfram_storage = """
{
    questions = (Map.empty :  (string, query_storage) map) ;
    owner = ("%s" : address)
}
""" % (owner)

wolfram_file = Path(__file__).parent / "wolfram.mligo"

def run_command(command):
    with Popen(command, stdout=PIPE, stderr=PIPE, shell=True) as p:
        with TextIOWrapper(p.stdout) as out, TextIOWrapper(p.stderr) as err:
            output = out.read()
            if not output:
                msg = err.read()
                raise Exception(msg)
            else:
                return output

def compile_contract():
    compile_command = f"{ligo_cmd} compile-contract {wolfram_file} main"
    result = run_command(compile_command)
    return result

def compile_storage():
    compile_command = f"{ligo_cmd} compile-storage {wolfram_file} main '{wolfram_storage}'"
    result = run_command(compile_command)
    return result

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


def get_contract_id(client, block_time, opg_hash, num_block_wait=2):
    for i in range(num_block_wait):
        wait_next_block(block_time, client)
        try:
           pending_opg = client.shell.mempool.pending_operations[opg_hash]
           if not OperationResult.is_applied(pending_opg):
                raise "Operation is pending"
           print(f'Still in mempool: {opg_hash}')
        except StopIteration:
            res = client.shell.blocks[-(i + 1):].find_operation(opg_hash)
            if not OperationResult.is_applied(res):
                raise "Operation was not applied"
            metadata = res['contents'][0]['metadata']
            contract_id = metadata['operation_result']['originated_contracts'][0]
            return contract_id


def setup_contract():
    print("compiling contract...")
    contract = compile_contract()
    contract = ContractInterface.from_michelson(contract).using(shell=shell, key=owner)
    contract.using(shell=shell, key=key)
    contract.originate(balance=5000000)
    print("originating contract...")
    payload = client.origination(
        contract.script()
    ).fill(
        counter=None, branch_offset=1
    ).sign().inject()
    print("contract was originated")
    operation_hash = payload['hash']
    contract_id = get_contract_id(client, 2, operation_hash)
    print(contract_id)
    return(contract_id)

setup_contract()
