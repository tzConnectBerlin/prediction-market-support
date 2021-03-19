import configparser

from pytezos import pytezos

class Config:
    def __init__(
            self,
            admin_account_key: str = None,
            config_file="oracle.ini",
            contract: str = "",
            endpoint: str = "",
            ipfs_server: str = None,
            user_folder: str = None
        ):
        """
        Init a config file
        """
        self.data={}
        if config_file is not None:
            config = configparser.ConfigParser()
            try:
                config.read(config_file)
            except Exception:
                print("Missing oracle.ini file")
        self.data["contract"] = contract or config['Tezos']['pm_contract']
        self.data["endpoint"] = endpoint or config['Tezos']['endpoint']
        self.data["ipfs_server"] = ipfs_server or config['IPFS']['server']
        privkey = admin_account_key or config['Tezos']['privkey']
        try:
            self.data["admin_account"] = pytezos.using(key=privkey, shell=self["endpoint"])
        except:
            print(f'Something went wrong with instantiating the shell object on endpoint {self["endpoint"]}')

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        return None
