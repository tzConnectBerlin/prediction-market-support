import os

from io import TextIOWrapper
from subprocess import Popen, PIPE

from loguru import logger


def ligo_cmd(wrkdir):
    if wrkdir == "":
        wrkdir = "$PWD"
    cmd = f'docker run --rm -v {wrkdir}:{wrkdir} -w {wrkdir} ligolang/ligo:0.14.0 "$@"'
    return cmd


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


def compile_contract(file, wrkdir=""):
    """
    Compile a contract and return the result

    :param file: path to the contract
    :return:
    """
    compile_command = f"{ligo_cmd(wrkdir)} compile-contract {file} main"
    result = run_command(compile_command)
    logger.debug(result)
    return result


def compile_storage(file, storage, wrkdir=""):
    """
    Compile the storage for a contract

    :param file: path to the contract
    :param storage:
    :return:
    """
    compile_command = f"{ligo_cmd(wrkdir)} compile-storage {file} main '{storage}'"
    result = run_command(compile_command)
    logger.debug(result)
    return result


def compile_expression(file, wrkdir=""):
    """
    Compile a file as an expression in cameligo

    :param file: path to the file to compile
    """
    compile_command = f"{ligo_cmd(wrkdir)} compile-expression --init-file={file} cameligo f"
    logger.debug(compile_command)
    result = run_command(compile_command)
    logger.debug(result)
    return result


def preprocess_file(file, helper_directory, wrkdir=""):
    """
    Preprocess a file to be compiled
    :param file: path to the preprocessing file
    :helper_directory: path to the folder containing the preprocessing files
    """
    file = file
    if wrkdir == "":
        wrkdir = os.path.split(file)[0]
    compile_command = f'm4 -P -I {helper_directory} -D "M4_WORKING_DIR={wrkdir}" {file}'
    result = run_command(compile_command)
    logger.debug(result)
    return result


def write_to_file(content, filepath):
    """
    Write to a file

    :param content: content to write to the file
    :param filepath: file to Write
    """
    f = open(filepath, "w")
    f.write(content)
    f.close()


def launch_sandbox():
    """
    Start the sandbox

    :return:
    """
    command = "sh sandbox/start_sandbox.sh"
    result = run_command(command)
    logger.debug(result)
    return result


def stop_sandbox():
    """
    Stop the sandbox

    :return:
    """
    command = "sh sandbox/stop_sandbox.sh"
    result = run_command(command)
    logger.debug(result)
    return result
