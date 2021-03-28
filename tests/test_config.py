import configparser
import pytest

from src.config import Config

loaded_config = configparser.ConfigParser()
loaded_config.read("tests/oracle.ini")

"""
@pytest.mark.parametrize("input,expected", [
    ["testnet", "testnet"],
    [None, "http://localhost:20000"]
])
def test_override_endpoint(input, expected):
    config = Config(
            config_file="tests/oracle.ini",
            endpoint=input,
    )
    assert config["endpoint"] == expected
    assert loaded_config["Tezos"]["pm_contract"] == config["contract"]
    assert loaded_config["IPFS"]["server"] == config["ipfs_server"]
    assert loaded_config["Tezos"]["privkey"] == config["admin_account"].key.secret_key()

@pytest.mark.parametrize("input,expected", [
    ["KT1KiAfhrT1HAFu8cG97G1woWGiq7Duoubk5", "KT1KiAfhrT1HAFu8cG97G1woWGiq7Duoubk5"],
    [None, loaded_config["Tezos"]["pm_contract"]]
])
def test_override_contract(input, expected):
    config = Config(
            config_file="tests/oracle.ini",
            contract=input
    )
    assert config["contract"] == expected
    assert loaded_config["Tezos"]["endpoint"] == config["endpoint"]
    assert loaded_config["IPFS"]["server"] == config["ipfs_server"]
    assert loaded_config["Tezos"]["privkey"] == config["admin_account"].key.secret_key()

@pytest.mark.parametrize("input,expected", [
    ["API /ip4/0.0.0.0/tcp/5001", "API /ip4/0.0.0.0/tcp/5001"],
    [None, loaded_config["IPFS"]["server"]]
])
def test_override_ipfsserver(input, expected):
    config = Config(
            config_file="tests/oracle.ini",
            ipfs_server=input,
    )
    assert config["ipfs_server"] == expected
    assert loaded_config["Tezos"]["endpoint"] == config["endpoint"]
    assert loaded_config["Tezos"]["pm_contract"] == config["contract"]
    assert loaded_config["Tezos"]["privkey"] == config["admin_account"].key.secret_key()

@pytest.mark.parametrize("input,expected", [
    ["edsk2sRikkzrGKnRC28UhvJsKAM19vuv4LtCRViyjkm2jMyAxiCMuG", "edsk2sRikkzrGKnRC28UhvJsKAM19vuv4LtCRViyjkm2jMyAxiCMuG"],
    [None, loaded_config["Tezos"]["privkey"]]
])
def test_override_admin_account(input, expected):
    config = Config(
            config_file="tests/oracle.ini",
            admin_account_key=input,
    )
    assert config["admin_account"].key.secret_key() == expected
    assert loaded_config["Tezos"]["endpoint"] == config["endpoint"]
    assert loaded_config["Tezos"]["pm_contract"] == config["contract"]
    assert loaded_config["IPFS"]["server"] == config["ipfs_server"]
"""
