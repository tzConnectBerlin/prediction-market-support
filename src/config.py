import configparser
import json
from pytezos import pytezos

class Config:
    def __init__(self,
            config_file="oracle.ini",
            contract: str = None,
            endpoint: str = None,
            ipfs_server: str = None,
            admin_account_key: str = None
        ):
        """
        Init a config file
        """
        if config_file is not None:
                config = configparser.ConfigParser()
            try:
                config.read(config_file)
            except Exception:
                print("Missing oracle.ini file")
        self.contract = config['Tezos']['pm_contract'] if contract else None
        self.endpoint = config['Tezos']['endpoint'] if endpoint else None
        self.ipfs_server = config['IPFS']['server'] if ipfs_server else None
        privkey = config['Tezos']['privkey'] if admin_account_key else None
        self.admin_account = pytezos(key=privkey, shell=self.endpoint)
