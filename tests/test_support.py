import sys

import pytest
from pytezos import pytezos, Key

from src.support.support import Support

support_instance = Support(
        ["donald"],
        config_file="./tests/oracle.ini",
        user_folder="./tests/users"
)

def test_users_is_imported():
    support_instance.import_user("donald")
    key = Key.from_alias("donald")
    assert key.public_key_hash() == "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"
    assert key.public_key() == "edpktqDLAmhcUAbztjBP7v8fyj5NGWU1G47kZrpvBY19TMLgjFRovR"
    assert key.secret_key() == "edsk2sRikkzrGKnRC28UhvJsKAM19vuv4LtCRViyjkm2jMyAxiCMuG"

def test_user_is_activated():
    support_instance.activate_user("donald")

def test_user_is_revealed():
    support_instance.activate_user("donald")

def test_get_user_account():
    key = support_instance.get_account("donald")
    assert key.public_key_hash() == "tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2"

def test_ask_question():
    support_instance.ask_question("who", "when", "donald", 30000, 10)

def test_transfer_stablecoin_to_user():
    support_instance.transfer_stablecoin_to_user("donald", 3000)

def bid_auction("):
