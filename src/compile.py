import os
from io import TextIOWrapper
from subprocess import Popen, PIPE

ligo_cmd = (
    f'docker run --rm -v "$PWD":"$PWD" -w "$PWD" ligolang/ligo:0.7.1 "$@"'
)


def run_command(command):
    """
    Run a command in a shell

    Caution, might not raise an error if the command doesn't return on stdout
    :param command:
    :return:
    """
    with Popen(command, stdout=PIPE, stderr=PIPE, shell=True) as p:
        with TextIOWrapper(p.stdout) as out, TextIOWrapper(p.stderr) as err:
            output = out.read()
            if not output:
                msg = err.read()
                raise Exception(msg)
            else:
                return output


def compile_contract(file):
    """
    Compile a contract and return the result

    :param file: path to the contract
    :return:
    """
    if os.path.exists(file) is False:
        raise Exception("File not found")

    compile_command = f"{ligo_cmd} compile-contract {file} main"
    result = run_command(compile_command)
    return result


def compile_storage(file, storage):
    """
    Compile the storage for a contract

    :param file: path to the contract
    :param storage:
    :return:
    """
    compile_command = f"{ligo_cmd} compile-storage {file} main '{storage}'"
    result = run_command(compile_command)
    return result


def launch_sandbox():
    """
    Start the sandbox

    :return:
    """
    command = "sh test/start_sandbox.sh"
    result = run_command(command)
    return result


def stop_sandbox():
    """
    Stop the sandbox

    :return:
    """
    command = "sh test/stop_sandbox.sh"
    result = run_command(command)
    return result
