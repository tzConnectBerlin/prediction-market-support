from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from subprocess import Popen, PIPE

from pytezos import pytezos, ContractInterface

ligo_cmd = (
        f'docker run --rm -v "$PWD":"$PWD" -w "$PWD" ligolang/ligo:0.7.1 "$@"'
)

def run_command(command):
    with Popen(command, stdout=PIPE, stderr=PIPE, shell=True) as p:
        with TextIOWrapper(p.stdout) as out, TextIOWrapper(p.stderr) as err:
            output = out.read()
            if not output:
                msg = err.read()
                raise Exception(msg)
            else:
                return output

def compile_contract(file):
    compile_command = f"{ligo_cmd} compile-contract {file} main"
    result = run_command(compile_command)
    return result

def compile_storage(file, storage):
    compile_command = f"{ligo_cmd} compile-storage {file} main '{storage}'"
    result = run_command(compile_command)
    return result

def launch_sandbox():
    command = "sh test/start_sandbox.sh"
    result = run_command(command)
    return result

def stop_sandbox():
    command = "sh test/stop_sandbox.sh"
    result = run_command(command)
    return result
