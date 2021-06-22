import configparser

from pytezos import pytezos

from loguru import logger

class Config:
    def __init__(
            self,
            admin_account_key: str = None,
            config_file='cli.ini',
            contract: str = '',
            endpoint: str = '',
            ipfs_server: str = None,
            stablecoin: str = None,
            user_folder: str = None
    ):
        """
        Init a config file
        """
        self.data = {}
        if config_file is not None:
            config = configparser.ConfigParser()
            try:
                config.read(config_file)
            except Exception:
                print('Missing cli.ini file')
        self.data['contract'] = contract or config['Tezos']['pm_contract']
        self.data['endpoint'] = endpoint or config['Tezos']['endpoint']
        self.data['ipfs_server'] = ipfs_server or config['IPFS']['server']
        self.data['stablecoin'] = stablecoin or config['Tezos']['stablecoin']
        self.data['contract_path'] = config['Tezos']['contract_path']
        self.data['stablecoin_path'] = config['Tezos']['stablecoin_path']
        self.data['admin_priv_key'] = admin_account_key or config['Tezos']['privkey']
        self.data['admin_account'] = None

    def get_admin_account(self):
        if self.data['admin_account'] is None:
            try:
                logger.error("in")
                self.data['admin_account'] = pytezos.using(
                    shell=self['endpoint']
                ).using(
                    key=self.data['admin_priv_key']
                )
            except Exception as _e:
                logger.error(f"Something went wrong with instantiating the shell object on endpoint {self['endpoint']}")
        return self.data['admin_account']

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        elif key == 'admin_account':
            return self.get_admin_account()
        return None
