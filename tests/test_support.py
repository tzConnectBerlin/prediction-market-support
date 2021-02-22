import sys
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
