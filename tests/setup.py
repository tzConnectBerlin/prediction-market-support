from io import TextIOWrapper
from pathlib import Path
from subprocess import Popen, PIPE

import pytest
import requests
from pytezos import pytezos, ContractInterface, Key 
from requests.exceptions import ConnectionError
from unittest import TestCase

from support import Support

ligo_cmd = (
        f'docker run --rm -v "$PWD":"$PWD" -w "$PWD" ligolang/ligo:0.7.1 "$@"'
)

shell="http://localhist:20000"

client = pytezos.using(
    shell=shell,
    key=Key.from_encoded_key(
        "edsk3RFgDiCt7tWB2oe96w1eRw72iYiiqZPLu9nnEY23MYRp2d8Kkx"
    )
)

owner = client.key.public_key_hash()

code = '(Pair {} "tz1YPSCGWXwBdTncK2aCctSZAXWvGsGwVJqU")'

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
    
class TestEx():
    def __init__(self):
        self.setup()

    def setup(self):
        print("compiling contract...")
        contract = compile_contract()
        self.contract = ContractInterface.from_michelson(contract).using(shell=shell, key=owner)
        self.contract.originate(balance=50000)
        self.mike_key = Key.generate(export=False)
        print("originating contract...")
        print(contract)

TestEx()
